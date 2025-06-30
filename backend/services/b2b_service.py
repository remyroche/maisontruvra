import json
import logging
from decimal import Decimal

from flask import url_for
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from backend.models.enums import UserType, NotificationType
from .exceptions import B2BAccountExistsError

from ..extensions import redis_client
from ..models import (db, B2BUser, User, Team, TeamMember, B2BInvitation, Tier,
                    Cart, Order, Product, OrderItem, Invoice, Company)
from ..models.enums import B2BStatus, NotificationType, UserType
from ..services.email_service import EmailService
from ..services.exceptions import (UserNotFoundError, NotFoundException, ServiceError)
from ..services.notification_service import NotificationService
from .monitoring_service import MonitoringService

from ..services.order_service import OrderService
from ..services.invoice_service import InvoiceService
from ..services.loyalty_service import LoyaltyService


logger = logging.getLogger(__name__)
CACHE_TTL_SECONDS = 600  # Cache for 10 minutes


class B2BService:
    """
    This service handles business logic for B2B users, including account management,
    teams, and B2B-specific commerce features like tiered pricing.
    """
  
    def __init__(self):
        self.order_service = OrderService()
        self.invoice_service = InvoiceService()
        self.loyalty_service = LoyaltyService()
      
    # --- B2B Account Management ---


    def get_b2b_user_dashboard(self, user_id):
        """
        Retrieves and aggregates comprehensive dashboard data for a B2B user.
        """
        b2b_user = B2BUser.query.filter_by(user_id=user_id).first()
        if not b2b_user:
            return None

        # --- Basic Information ---
        company = b2b_user.company
        recent_orders_paginated = self.order_service.get_user_orders(user_id, page=1, per_page=5)
        recent_orders = [order.to_dict() for order in recent_orders_paginated.items]
        recent_invoices_paginated = self.invoice_service.get_user_invoices(user_id, page=1, per_page=5)
        recent_invoices = [invoice.to_dict() for invoice in recent_invoices_paginated.items]

        # --- Key Performance Indicators (KPIs) ---
        total_spend = db.session.query(func.sum(Order.total_amount)).filter(Order.user_id == user_id).scalar() or 0
        total_orders = db.session.query(func.count(Order.id)).filter(Order.user_id == user_id).scalar() or 0

        # --- Loyalty and Referral Analytics ---
        loyalty_data = self.loyalty_service.get_user_loyalty_status(user_id)
        points_from_purchases = db.session.query(func.sum(LoyaltyTransaction.points)).filter(
            LoyaltyTransaction.user_id == user_id, 
            LoyaltyTransaction.reason.ilike('%purchase%')
        ).scalar() or 0
        points_from_referrals = db.session.query(func.sum(LoyaltyTransaction.points)).filter(
            LoyaltyTransaction.user_id == user_id,
            LoyaltyTransaction.reason.ilike('%referral%')
        ).scalar() or 0
        successful_referrals = Referral.query.filter_by(referrer_id=user_id).count()

        # --- Frequently Ordered Products ---
        top_product_ids = db.session.query(
            OrderItem.product_id, 
            func.count(OrderItem.product_id).label('purchase_count')
        ).join(Order).filter(Order.user_id == user_id).group_by(OrderItem.product_id).order_by(func.desc('purchase_count')).limit(5).all()
        
        frequently_ordered_products = []
        if top_product_ids:
            product_ids = [item[0] for item in top_product_ids]
            top_products = Product.query.filter(Product.id.in_(product_ids)).all()
            # Create a dictionary for quick lookups
            product_map = {p.id: p for p in top_products}
            for pid, count in top_product_ids:
                if pid in product_map:
                    product_data = product_map[pid].to_dict()
                    product_data['purchase_count'] = count
                    frequently_ordered_products.append(product_data)

        # --- Assemble the complete dashboard data ---
        dashboard_data = {
            "company_name": company.name,
            "recent_orders": recent_orders,
            "recent_invoices": recent_invoices,
            "analytics": {
                "total_spend": total_spend,
                "total_orders": total_orders,
                "frequently_ordered_products": frequently_ordered_products
            },
            "loyalty": {
                "total_points": loyalty_data.get('points', 0),
                "tier": loyalty_data.get('tier', 'N/A'),
                "points_from_purchases": points_from_purchases,
                "points_from_referrals": points_from_referrals,
                "successful_referrals": successful_referrals
            }
        }
        return dashboard_data


    @staticmethod
    def create_b2b_account(user: User, company_name: str, vat_number: str) -> B2BUser:
        """Creates a pending B2B account for an existing user."""
        if B2BUser.query.filter_by(user_id=user.id).first():
            raise B2BAccountExistsError("B2B account already exists for this user.")

        new_b2b_user = B2BUser(
            user_id=user.id,
            company_name=company_name,
            vat_number=vat_number,
            status=B2BStatus.PENDING
        )
        user.user_type = UserType.B2B
        db.session.add(new_b2b_user)
        db.session.add(user)
        db.session.commit()

        NotificationService.create_notification(
            user_id=None,
            message=f"New B2B account application from {company_name}.",
            notification_type=NotificationType.ADMIN_ALERT
        )
        EmailService.send_b2b_pending_approval_email(user.email, user.first_name)

        return new_b2b_user

    @staticmethod
    def get_all_b2b_users_with_details():
        """Retrieves all B2B users with their associated user and tier details."""
        return db.session.query(B2BUser).options(
            joinedload(B2BUser.user),
            joinedload(B2BUser.tier)
        ).all()

    @staticmethod
    def update_b2b_status(b2b_user_id: int, status: B2BStatus) -> B2BUser:
        """Updates the status of a B2B account."""
        b2b_user = db.session.query(B2BUser).options(joinedload(B2BUser.user)).get(b2b_user_id)
        if not b2b_user:
            raise NotFoundException("B2B account not found.")
        
        b2b_user.status = status
        db.session.commit()
        
        if status == B2BStatus.APPROVED:
            EmailService.send_b2b_account_approved_email(b2b_user.user.email, b2b_user.user.first_name)
            NotificationService.create_notification(
                user_id=b2b_user.user_id,
                message="Congratulations! Your B2B account has been approved.",
                notification_type=NotificationType.B2B_ACCOUNT_APPROVED
            )
        # Add other notifications for rejected, suspended, etc. if needed

        return b2b_user

    @staticmethod
    def get_b2b_user(user_id: int) -> B2BUser:
        """Retrieves the B2BUser profile for a given user ID, ensuring the user is B2B."""
        user = db.session.get(User, user_id)
        if not user or user.user_type != UserType.B2B or not user.b2b_user:
            raise NotFoundException("B2B profile not found for this user.")
        return user.b2b_user

    @staticmethod
    def update_company_profile_by_user(user_id: int, data: dict) -> B2BUser:
        """Updates a B2B user's company profile."""
        profile = B2BService.get_b2b_user(user_id)
        for key, value in data.items():
            if hasattr(profile, key) and key not in ['id', 'user_id']:
                setattr(profile, key, value)
        db.session.commit()
        return profile

    # --- Tier Management ---

    @staticmethod
    def create_tier(name: str, discount_percentage: Decimal, minimum_spend: Decimal = None) -> Tier:
        """Creates a new B2B pricing tier."""
        new_tier = Tier(
            name=name,
            discount_percentage=Decimal(discount_percentage),
            minimum_spend=Decimal(minimum_spend) if minimum_spend else None
        )
        db.session.add(new_tier)
        db.session.commit()
        return new_tier

    @staticmethod
    def get_tier(tier_id: int) -> Tier:
        """Retrieves a tier by its ID."""
        return db.session.query(Tier).get(tier_id)

    @staticmethod
    def get_all_tiers() -> list[Tier]:
        """Retrieves all tiers."""
        return db.session.query(Tier).all()

    @staticmethod
    def update_tier(tier_id: int, name: str = None, discount_percentage: Decimal = None, minimum_spend: Decimal = None) -> Tier:
        """Updates a tier's details."""
        tier = B2BService.get_tier(tier_id)
        if tier:
            if name is not None:
                tier.name = name
            if discount_percentage is not None:
                tier.discount_percentage = Decimal(discount_percentage)
            if minimum_spend is not None:
                tier.minimum_spend = Decimal(minimum_spend)
            db.session.commit()
        return tier

    @staticmethod
    def assign_tier_to_b2b_user(b2b_user_id: int, tier_id: int) -> B2BUser:
        """Assigns a pricing tier to a B2B user."""
        b2b_user = db.session.query(B2BUser).get(b2b_user_id)
        tier = B2BService.get_tier(tier_id)
        if b2b_user and tier:
            b2b_user.tier = tier
            db.session.commit()
            return b2b_user
        return None

    # --- B2B Commerce (Cart, Pricing, Order) ---
    
    @staticmethod
    def get_b2b_price(user: User, product: Product) -> Decimal:
        """
        Calculates the B2B price for a product based on the user's assigned tier.
        Uses Redis for caching.
        """
        if not user or user.user_type != UserType.B2B or not user.b2b_user or not user.b2b_user.tier_id:
            return product.price

        tier_id = user.b2b_user.tier_id
        cache_key = f"b2b_price:tier_{tier_id}:product_{product.id}"

        try:
            cached_price = redis_client.get(cache_key)
            if cached_price:
                return Decimal(cached_price.decode('utf-8'))
        except Exception as e:
            MonitoringService.log_error(f"Redis GET error for key {cache_key}: {e}", "B2BService", level='WARNING')

        tier = db.session.get(Tier, tier_id)
        if not tier or tier.discount_percentage <= 0:
            calculated_price = product.price
        else:
            discount = (product.price * tier.discount_percentage) / Decimal(100)
            calculated_price = product.price - discount

        try:
            redis_client.setex(cache_key, CACHE_TTL_SECONDS, str(calculated_price))
        except Exception as e:
            MonitoringService.log_error(f"Redis SETEX error for key {cache_key}: {e}", "B2BService", level='WARNING')

        return calculated_price.quantize(Decimal("0.01"))

    @staticmethod
    def get_b2b_cart(user_id: int) -> Cart:
        """Gets or creates a cart record for a B2B user."""
        b2b_profile = B2BService.get_b2b_user(user_id)
        cart = Cart.query.filter_by(b2b_account_id=b2b_profile.id).first()
        if not cart:
            cart = Cart(user_id=user_id, b2b_account_id=b2b_profile.id)
            db.session.add(cart)
            db.session.commit()
        return cart

    @staticmethod
    def get_cart_with_b2b_pricing(user_id: int) -> dict:
        """
        Retrieves a user's cart and calculates prices, including B2B tier discounts.
        """
        user = db.session.query(User).options(
            joinedload(User.b2b_user).joinedload(B2BUser.tier),
            joinedload(User.carts).joinedload('items').joinedload('product')
        ).get(user_id)

        if not user or not user.carts:
            return None

        cart = user.carts[0]

        if user.user_type == UserType.B2B and user.b2b_user and user.b2b_user.tier:
            tier = user.b2b_user.tier
            discount_multiplier = Decimal('1') - (tier.discount_percentage / Decimal('100'))

            items_details = []
            subtotal = Decimal('0.00')
            for item in cart.items:
                original_price = item.price
                discounted_price = (original_price * discount_multiplier).quantize(Decimal('0.01'))
                subtotal += original_price * item.quantity
                items_details.append({
                    'item': item,
                    'original_price': original_price,
                    'discounted_price': discounted_price,
                    'line_total': discounted_price * item.quantity
                })
            
            total = sum(i['line_total'] for i in items_details)
            discount_applied = subtotal - total

            return {
                'cart': cart, 'items_details': items_details, 'subtotal': subtotal,
                'discount_applied': discount_applied, 'total': total, 'tier_name': tier.name
            }

        subtotal = sum(item.price * item.quantity for item in cart.items)
        return {
            'cart': cart,
            'items_details': [{
                'item': item, 'original_price': item.price, 'discounted_price': item.price,
                'line_total': item.price * item.quantity
            } for item in cart.items],
            'subtotal': subtotal, 'discount_applied': Decimal('0.00'),
            'total': subtotal, 'tier_name': None
        }

    @staticmethod
    def create_b2b_order(user_id: int, shipping_address_id: int, billing_address_id: int) -> Order:
        """Creates a B2B order from the user's cart, applying B2B pricing."""
        user = db.session.query(User).options(joinedload(User.b2b_user)).get(user_id)
        if not user or user.user_type != UserType.B2B:
            raise NotFoundException("B2B user not found")

        cart = B2BService.get_b2b_cart(user_id)
        if not cart.items:
            raise ServiceError("Cannot create an order from an empty cart.", 400)

        total_cost = Decimal(0)
        order_items = []
        for item in cart.items:
            product_price = B2BService.get_b2b_price(user, item.product)
            total_cost += product_price * item.quantity
            order_items.append(OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=product_price
            ))

        new_order = Order(
            user_id=user_id,
            b2b_account_id=user.b2b_user.id,
            total_cost=total_cost,
            items=order_items,
            shipping_address_id=shipping_address_id,
            billing_address_id=billing_address_id,
            user_type=UserType.B2B
        )

        db.session.add(new_order)
        for item in cart.items:
            db.session.delete(item)

        db.session.commit()
        MonitoringService.log_info(f"B2B Order {new_order.id} created for account {user.b2b_user.id}", "B2BService")
        return new_order

    @staticmethod
    def get_b2b_invoices_paginated(user_id: int, page: int, per_page: int):
        """Retrieves a paginated list of invoices for a B2B account."""
        account = B2BService.get_b2b_user(user_id)
        return Invoice.query.filter_by(b2b_account_id=account.id).order_by(Invoice.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

