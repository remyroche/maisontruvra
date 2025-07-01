from decimal import Decimal
from sqlalchemy.orm import joinedload

from ..models import db, User, Product, Order, OrderItem, Cart, Tier, Discount
from ..models.enums import UserType
from ..services.exceptions import NotFoundException, ServiceError
from ..services.monitoring_service import MonitoringService
from ..extensions import redis_client
from datetime import datetime
from ..services.exceptions import DiscountInvalidException
from backend.utils.input_sanitizer import sanitize_plaintext

from backend.models.discount_models import Discount
from backend.database import db
from backend.utils.input_sanitizer import sanitize_input
from flask import current_app


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
    def create_discount(data):
        """ Creates a discount with a sanitized code. """
        sanitized_code = sanitize_input(data['code']).upper()
        
        if Discount.query.filter_by(code=sanitized_code).first():
            raise ValueError("A discount with this code already exists.")

        new_discount = Discount(
            code=sanitized_code,
            discount_type=data['discount_type'],
            value=data['value'],
            expires_at=data.get('expires_at'),
            max_uses=data.get('max_uses'),
            min_purchase_amount=data.get('min_purchase_amount')
        )
        db.session.add(new_discount)
        db.session.commit()
        current_app.logger.info(f"New discount created: {sanitized_code}")
        return new_discount


    @staticmethod
    def get_discount_by_code(code):
        """Retrieves a discount by its code."""
        sanitized_code = sanitize_plaintext(code).upper()
        return Discount.query.filter_by(code=sanitized_code).first()

    
    @staticmethod
    def apply_discount_code(self, cart, code):
        """
        Applies a discount code to a cart.
        Validates the discount against the database and calculates the new total.
        """
        # Find the discount by its code, ensuring it is active.
        discount = Discount.query.filter_by(code=code, is_active=True).first()

        if not discount:
            raise DiscountInvalidException("Discount code not found or is not active.")

        # Check if the discount has expired.
        if discount.expiry_date and discount.expiry_date < datetime.utcnow():
            raise DiscountInvalidException("Discount code has expired.")

        # Check if the discount has reached its usage limit.
        if discount.usage_limit is not None and discount.times_used >= discount.usage_limit:
            raise DiscountInvalidException("Discount code has reached its usage limit.")

        # TODO: Add logic to check for user-specific or product-specific discounts if needed.

        # Calculate the actual discount amount based on its type.
        discount_amount = 0
        if discount.discount_type == 'percentage':
            discount_amount = (cart.total_cost * discount.value) / 100
        elif discount.discount_type == 'fixed_amount':
            discount_amount = discount.value
        
        # Ensure the discount doesn't make the cart total negative.
        discount_amount = min(discount_amount, cart.total_cost)

        # Apply the discount to the cart.
        cart.discount_amount = discount_amount
        cart.total_cost -= discount_amount
        cart.applied_discount_code = code

        # Increment the usage count for the discount.
        discount.times_used += 1
        
        db.session.commit()

        return {
            "success": True, 
            "message": "Discount applied successfully.",
            "new_total": cart.total_cost,
            "discount_amount": cart.discount_amount
        }

    @staticmethod
    def remove_discount_from_cart(self, cart):
        """Removes a discount from the cart and reverts the total cost."""
        if not cart.applied_discount_code:
            return {"success": False, "message": "No discount to remove."}

        discount = Discount.query.filter_by(code=cart.applied_discount_code).first()

        # If the discount exists, revert the cost and decrement its usage count.
        if discount:
            cart.total_cost += cart.discount_amount
            if discount.times_used > 0:
                 discount.times_used -= 1
        
        cart.discount_amount = 0.0
        cart.applied_discount_code = None
        
        db.session.commit()
        return {"success": True, "message": "Discount removed."}

    
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
    def update_discount(self, discount_id, data):
        """ Updates a discount with sanitized fields. """
        discount = Discount.query.get(discount_id)
        if not discount:
            return None

        if 'code' in data:
            sanitized_code = sanitize_input(data['code']).upper()
            if Discount.query.filter(Discount.id != discount_id, Discount.code == sanitized_code).first():
                 raise ValueError("A discount with this code already exists.")
            discount.code = sanitized_code
        
        for field in ['discount_type', 'value', 'expires_at', 'max_uses', 'min_purchase_amount']:
            if field in data:
                setattr(discount, field, data[field])

        db.session.commit()
        current_app.logger.info(f"Discount {discount_id} updated.")
        return discount


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
