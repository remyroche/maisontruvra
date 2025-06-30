from decimal import Decimal
from sqlalchemy.orm import joinedload

from ..models import db, User, Product, Order, OrderItem, Cart, Tier
from ..models.enums import UserType
from ..services.exceptions import NotFoundException, ServiceError
from ..services.monitoring_service import MonitoringService
from ..extensions import redis_client

CACHE_TTL_SECONDS = 600

class DiscountService:
    """
    This service handles all pricing and discount logic for all users (B2C and B2B).
    """

    # --- Tier Management (Now for all users) ---
    
    @staticmethod
    def create_tier(name: str, discount_percentage: Decimal, minimum_spend: Decimal = None) -> Tier:
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
        return db.session.query(Tier).get(tier_id)

    @staticmethod
    def get_all_tiers() -> list[Tier]:
        return db.session.query(Tier).all()

    @staticmethod
    def assign_tier_to_user(user_id: int, tier_id: int) -> User:
        """Manually assigns a pricing tier to any user and sets an override flag."""
        user = db.session.query(User).get(user_id)
        tier = DiscountService.get_tier(tier_id)
        if not user or not tier:
            raise NotFoundException("User or Tier not found.")
        
        user.tier = tier
        user.tier_override = True  # Manual assignment overrides automated logic
        db.session.commit()
        return user

    # --- Custom Discount Management (Now for all users) ---

    @staticmethod
    def set_custom_discount_for_user(user_id: int, discount_percentage: Decimal, spend_limit: Decimal):
        """Sets a custom discount percentage and monthly spend limit for any user."""
        user = db.session.query(User).get(user_id)
        if not user:
            raise NotFoundException("User not found")
        
        user.custom_discount_percentage = discount_percentage
        user.monthly_spend_limit = spend_limit
        user.tier_override = True  # Custom discount is a form of manual override
        db.session.commit()
        return user

    # --- Pricing and Order Logic ---

    @staticmethod
    def get_price(user: User, product: Product) -> Decimal:
        """
        Calculates the price for a product for any given user.
        Priority:
        1. User's custom discount (if spend limit not exceeded).
        2. User's tier-based discount.
        3. Standard product price.
        """
        # 1. Check for custom discount
        if (user.custom_discount_percentage is not None and 
            user.monthly_spend_limit is not None):
            
            if user.current_monthly_spend < user.monthly_spend_limit:
                discount_multiplier = Decimal('1') - (user.custom_discount_percentage / Decimal('100'))
                return (product.price * discount_multiplier).quantize(Decimal("0.01"))

        # 2. Fallback to tier-based discount
        if user.tier_id:
            cache_key = f"price:tier_{user.tier_id}:product_{product.id}"
            try:
                cached_price = redis_client.get(cache_key)
                if cached_price:
                    return Decimal(cached_price.decode('utf-8'))
            except Exception as e:
                MonitoringService.log_error(f"Redis GET error for key {cache_key}: {e}", "DiscountService", level='WARNING')
            
            tier = user.tier
            if tier and tier.discount_percentage > 0:
                discount = (product.price * tier.discount_percentage) / Decimal(100)
                calculated_price = (product.price - discount).quantize(Decimal("0.01"))
                try:
                    redis_client.setex(cache_key, CACHE_TTL_SECONDS, str(calculated_price))
                except Exception as e:
                    MonitoringService.log_error(f"Redis SETEX error for key {cache_key}: {e}", "DiscountService", level='WARNING')
                return calculated_price
        
        # 3. Standard price
        return product.price

    @staticmethod
    def create_order(user_id: int, shipping_address_id: int, billing_address_id: int) -> Order:
        """Creates an order and updates the user's monthly spend if applicable."""
        user = db.session.query(User).options(joinedload(User.tier)).get(user_id)
        if not user:
            raise NotFoundException("User not found")

        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart or not cart.items:
            raise ServiceError("Cannot create an order from an empty cart.", 400)

        total_cost = Decimal(0)
        order_items = []
        
        for item in cart.items:
            # Use the unified get_price method
            product_price = DiscountService.get_price(user, item.product)
            line_total = product_price * item.quantity
            total_cost += line_total
            order_items.append(OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=product_price
            ))

        new_order = Order(
            user_id=user_id,
            total_cost=total_cost,
            items=order_items,
            shipping_address_id=shipping_address_id,
            billing_address_id=billing_address_id,
            user_type=user.user_type
        )

        # Update monthly spend for users with custom discounts
        if user.custom_discount_percentage is not None:
            user.current_monthly_spend += total_cost
        
        db.session.add(new_order)
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()

        MonitoringService.log_info(f"Order {new_order.id} created for user {user_id}", "DiscountService")
        # NOTE: A scheduled monthly task should reset `current_monthly_spend`.
        return new_order
