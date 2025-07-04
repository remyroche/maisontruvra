from datetime import datetime
from decimal import Decimal

from sqlalchemy.exc import SQLAlchemyError

from backend.database import db
from backend.extensions import db
from backend.models import Discount

from ..models import Discount, Tier, User, db
from ..services.exceptions import DiscountInvalidException, NotFoundException

CACHE_TTL_SECONDS = 600


class DiscountService:
    """
    This service handles all pricing and discount logic for all users (B2C and B2B).
    """

    def __init__(self, logger):
        self.logger = logger

    # --- Tier Management (Now for all users) ---

    @staticmethod
    def create_tier(
        name: str, discount_percentage: Decimal, minimum_spend: Decimal = None
    ) -> Tier:
        new_tier = Tier(
            name=name,
            discount_percentage=Decimal(discount_percentage),
            minimum_spend=Decimal(minimum_spend) if minimum_spend else None,
        )
        db.session.add(new_tier)
        db.session.commit()
        return new_tier

    def create_discount(self, discount_data):
        """Creates a new discount."""
        try:
            discount = Discount(**discount_data)
            db.session.add(discount)
            db.session.commit()
            self.logger.info(f"Discount '{discount.code}' created successfully.")
            return discount
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"Error creating discount: {e}")
            raise

    def get_discount_by_code(self, code):
        """Retrieves a discount by its code."""
        return db.session.query(Discount).filter_by(code=code).first()

    def get_all_discounts(self):
        """Retrieves all discounts."""
        return db.session.query(Discount).all()

    def is_discount_valid(self, discount):
        """Checks if a discount is active, not expired, and has uses left."""
        if not discount.is_active:
            return False
        if discount.expires_at and discount.expires_at < datetime.utcnow():
            return False
        if discount.max_uses is not None and discount.times_used >= discount.max_uses:
            return False
        return True

    def record_discount_usage(self, discount_id):
        """
        Increments the usage count for a given discount.
        This should be called after a successful order placement.
        """
        try:
            # Lock the row for update to prevent race conditions
            discount = (
                db.session.query(Discount)
                .with_for_update()
                .filter_by(id=discount_id)
                .first()
            )

            if discount and discount.max_uses is not None:
                discount.times_used = (discount.times_used or 0) + 1
                if discount.times_used > discount.max_uses:
                    self.logger.warning(
                        f"Discount {discount_id} usage has now exceeded its max limit."
                    )
                db.session.commit()
                self.logger.info(f"Usage recorded for discount {discount_id}.")

        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"Error recording usage for discount {discount_id}: {e}")
            raise

    def update_discount(self, discount_id, update_data):
        """Updates an existing discount."""
        try:
            discount = db.session.query(Discount).get(discount_id)
            if discount:
                for key, value in update_data.items():
                    setattr(discount, key, value)
                db.session.commit()
                self.logger.info(f"Discount {discount_id} updated.")
                return discount
            return None
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"Error updating discount {discount_id}: {e}")
            raise

    def delete_discount(self, discount_id):
        """Deletes a discount."""
        try:
            discount = db.session.query(Discount).get(discount_id)
            if discount:
                db.session.delete(discount)
                db.session.commit()
                self.logger.info(f"Discount {discount_id} deleted.")
                return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"Error deleting discount {discount_id}: {e}")
            raise

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
        if (
            discount.usage_limit is not None
            and discount.times_used >= discount.usage_limit
        ):
            raise DiscountInvalidException("Discount code has reached its usage limit.")

        # TODO: Add logic to check for user-specific or product-specific discounts if needed.

        # Calculate the actual discount amount based on its type.
        discount_amount = 0
        if discount.discount_type == "percentage":
            discount_amount = (cart.total_cost * discount.value) / 100
        elif discount.discount_type == "fixed_amount":
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
            "discount_amount": cart.discount_amount,
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
    def set_custom_discount_for_user(
        user_id: int, discount_percentage: Decimal, spend_limit: Decimal
    ):
        """Sets a custom discount percentage and monthly spend limit for any user."""
        user = db.session.query(User).get(user_id)
        if not user:
            raise NotFoundException("User not found")

        user.custom_discount_percentage = discount_percentage
        user.monthly_spend_limit = spend_limit
        user.tier_override = True  # Custom discount is a form of manual override
        db.session.commit()
        return user
