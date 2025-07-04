import logging
from decimal import Decimal
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from backend.database import db
from backend.models import (
    User,
    Cart,
    CartItem,
    Product,
    ExclusiveReward,
    InventoryReservation,
)
from backend.models.enums import UserType
from backend.services.exceptions import (
    NotFoundException,
    ServiceError,
    ValidationException,
    PermissionError,
)
from backend.services.inventory_service import InventoryService
from backend.utils.input_sanitizer import InputSanitizer

class CartService:
    """A comprehensive service for all cart-related operations."""

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def _get_or_create_cart(self, user_id: int) -> Cart:
        """Private helper to retrieve a user's cart, creating one if it doesn't exist."""
        cart = Cart.query.filter_by(user_id=user_id, is_active=True).first()
        if not cart:
            self.logger.info(f"No active cart found for user {user_id}. Creating a new one.")
            cart = Cart(user_id=user_id)
            db.session.add(cart)
            # We don't commit here; the calling function will handle the transaction.
            db.session.flush() # Flush to get the cart ID
        return cart

    def get_cart_details(self, user_id: int) -> dict:
        """
        Retrieves full cart details for a user, applying B2B tiered pricing if applicable.
        This is the primary method for fetching the current state of a user's cart.
        """
        user = User.query.options(
            joinedload(User.tier),
            joinedload(User.carts).joinedload(Cart.items).joinedload(CartItem.product)
        ).get(user_id)

        if not user:
            raise NotFoundException("User not found.")

        cart = next((c for c in user.carts if c.is_active), None)
        if not cart:
            return { "items": [], "subtotal": "0.00", "total": "0.00", "discount": "0.00" }

        items_details = []
        subtotal = Decimal("0.00")
        discount_multiplier = Decimal("1.0")

        if user.user_type == UserType.B2B and user.tier:
            discount_multiplier = Decimal("1") - (user.tier.discount_percentage / Decimal("100"))

        for item in cart.items:
            original_price = item.product.price
            # Rewards are free
            final_price = Decimal("0.00") if item.is_reward else (original_price * discount_multiplier).quantize(Decimal("0.01"))
            line_total = final_price * item.quantity
            items_details.append({
                "item_id": item.id,
                "product_id": item.product.id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "is_reward": item.is_reward,
                "final_price": str(final_price),
                "line_total": str(line_total),
            })
            subtotal += original_price * item.quantity

        total = sum(Decimal(i["line_total"]) for i in items_details)
        total_discount = subtotal - total

        return {
            "cart_id": cart.id,
            "items": items_details,
            "subtotal": str(subtotal.quantize(Decimal("0.01"))),
            "discount": str(total_discount.quantize(Decimal("0.01"))),
            "total": str(total.quantize(Decimal("0.01"))),
            "tier_name": user.tier.name if user.user_type == UserType.B2B and user.tier else None,
        }

    def add_item(self, user_id: int, product_id: int, quantity: int, custom_price: Decimal = None) -> Cart:
        """Adds an item to a user's cart, handling stock reservation and ownership."""
        quantity = int(quantity)
        if quantity <= 0:
            raise ValidationException("Quantity must be a positive integer.")

        product = Product.query.get(product_id)
        if not product:
            raise NotFoundException("Product not found.")

        if product.owner_id and product.owner_id != user_id:
            self.logger.warning(f"User {user_id} attempted to add exclusive product {product_id}.")
            raise PermissionError("This product is exclusive and cannot be added to your cart.")

        cart = self._get_or_create_cart(user_id)
        
        # Reserve stock before making changes
        InventoryService.reserve_stock(product_id, quantity, user_id)

        try:
            cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id, is_reward=False).first()
            if cart_item:
                cart_item.quantity += quantity
            else:
                price = custom_price if custom_price is not None else product.price
                cart_item = CartItem(
                    cart_id=cart.id,
                    product_id=product_id,
                    quantity=quantity,
                    price_at_addition=price
                )
                db.session.add(cart_item)
            
            db.session.commit()
            self.logger.info(f"Added {quantity} of product {product_id} to cart for user {user_id}.")
            return cart
        except Exception as e:
            db.session.rollback()
            # Release stock if cart operation fails
            InventoryService.release_stock(product_id, quantity, user_id)
            self.logger.error(f"Failed to add item to cart for user {user_id}: {e}", exc_info=True)
            raise ServiceError("Could not add item to cart.") from e

    def update_item_quantity(self, user_id: int, item_id: int, new_quantity: int) -> Cart:
        """Updates an item's quantity in the cart and adjusts inventory reservations."""
        new_quantity = int(new_quantity)
        if new_quantity <= 0:
            return self.remove_item(user_id, item_id)

        cart_item = CartItem.query.join(Cart).filter(Cart.user_id == user_id, CartItem.id == item_id).first()
        if not cart_item:
            raise NotFoundException("Cart item not found.")

        quantity_diff = new_quantity - cart_item.quantity
        if quantity_diff == 0:
            return cart_item.cart

        try:
            if quantity_diff > 0:
                InventoryService.reserve_stock(cart_item.product_id, quantity_diff, user_id)
            else: # quantity_diff < 0
                InventoryService.release_stock(cart_item.product_id, -quantity_diff, user_id)
            
            cart_item.quantity = new_quantity
            db.session.commit()
            self.logger.info(f"Updated cart item {item_id} to quantity {new_quantity} for user {user_id}.")
            return cart_item.cart
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to update cart item {item_id}: {e}", exc_info=True)
            raise ServiceError("Failed to update cart item.") from e

    def remove_item(self, user_id: int, item_id: int) -> Cart:
        """Removes an item from the cart and releases its inventory reservation."""
        cart_item = CartItem.query.join(Cart).filter(Cart.user_id == user_id, CartItem.id == item_id).first()
        if not cart_item:
            # Item is already gone, so the operation is successful in its outcome.
            cart = Cart.query.filter_by(user_id=user_id).first()
            return cart

        quantity_to_release = cart_item.quantity
        product_id = cart_item.product_id
        cart = cart_item.cart
        
        try:
            db.session.delete(cart_item)
            InventoryService.release_stock(product_id, quantity_to_release, user_id)
            db.session.commit()
            self.logger.info(f"Removed item {item_id} from cart for user {user_id}.")
            return cart
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to remove cart item {item_id}: {e}", exc_info=True)
            raise ServiceError("Failed to remove cart item.") from e

    def clear_cart(self, user_id: int) -> bool:
        """Clears all items and inventory reservations for a user's cart."""
        cart = Cart.query.filter_by(user_id=user_id, is_active=True).first()
        if not cart:
            return True

        try:
            InventoryReservation.query.filter_by(user_id=user_id).delete(synchronize_session=False)
            CartItem.query.filter_by(cart_id=cart.id).delete(synchronize_session=False)
            db.session.commit()
            self.logger.info(f"Cart and reservations cleared for user {user_id}.")
            return True
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to clear cart for user {user_id}: {e}", exc_info=True)
            raise ServiceError("Failed to clear cart due to a database error.") from e

    def add_reward_to_cart(self, user_id: int, reward_id: int) -> Cart:
        """Adds a redeemed loyalty reward product to the user's cart."""
        cart = self._get_or_create_cart(user_id)
        reward = ExclusiveReward.query.get(reward_id)

        if not reward or not reward.linked_product_id:
            raise ValidationException("Reward is not a product and cannot be added to the cart.")

        try:
            new_item = CartItem(
                cart_id=cart.id,
                product_id=reward.linked_product_id,
                quantity=1,
                is_reward=True,
                price_at_addition=Decimal("0.00")
            )
            db.session.add(new_item)
            db.session.commit()
            self.logger.info(f"Added reward {reward_id} to cart for user {user_id}.")
            return cart
        except IntegrityError as e:
            db.session.rollback()
            self.logger.warning(f"Attempted to add duplicate reward {reward_id} to cart for user {user_id}.")
            raise ValidationException("This reward is already in your cart.") from e
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to add reward to cart: {e}", exc_info=True)
            raise ServiceError("Could not add reward to cart.") from e
