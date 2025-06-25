from flask import current_app
from flask_login import current_user
from backend.database import db
from backend.models.cart_models import Cart, CartItem
from backend.models.product_models import Product, ProductVariant
from backend.models.inventory_models import InventoryReservation # Added: Import InventoryReservation
from .exceptions import ServiceError, ValidationException, NotFoundException
from .inventory_service import InventoryService
from backend.utils.input_sanitizer import InputSanitizer

class CartService:
    @staticmethod
    def get_cart_for_user(user_id):
        """Finds or creates a cart for a given user."""
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            db.session.add(cart)
            # We commit here to get a cart ID for new carts.
            # Subsequent operations in the same request will be part of a new transaction.
            db.session.commit()
        return cart

    @staticmethod
    def add_to_cart(cart_data: dict):
        """Add item to cart with validation and inventory reservation."""
        cart_data = InputSanitizer.sanitize_json(cart_data)
        
        if not current_user.is_authenticated:
            raise ServiceError("User must be authenticated", 401)
        user_id = current_user.id
        
        if not cart_data.get('product_id') or not cart_data.get('quantity'):
            raise ValidationException("product_id and quantity are required")
            
        product_id = cart_data['product_id']
        try:
            quantity = int(cart_data['quantity'])
            if quantity <= 0:
                raise ValidationException("Quantity must be positive")
        except (ValueError, TypeError):
            raise ValidationException("Quantity must be a valid number")

        product = Product.query.get(product_id)
        if not product:
            raise NotFoundException(f"Product with ID {product_id} not found")

        # --- Reservation Logic ---
        try:
            InventoryService.reserve_stock(product_id, quantity, user_id=user_id)
        except ServiceError as e:
            current_app.logger.warning(f"Failed to reserve stock for product {product_id} for user {user_id}: {e.message}")
            raise e # Re-raise to inform the client of the stock issue
        # --- End Reservation Logic ---

        try:
            cart = CartService.get_cart_for_user(user_id)
            existing_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
            
            if existing_item:
                existing_item.quantity += quantity
            else:
                new_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
                db.session.add(new_item)
            
            db.session.commit()
            current_app.logger.info(f"Item added to cart: User {user_id}, Product {product_id}, Quantity {quantity}")
            return cart.to_dict() # Return the updated cart
        except Exception as e:
            db.session.rollback()
            # If DB operation fails, we must release the reservation
            InventoryService.release_stock(product_id, quantity, user_id=user_id)
            current_app.logger.error(f"Failed to add item to cart after reservation: {str(e)}", exc_info=True)
            raise ServiceError(f"Failed to add item to cart: {str(e)}")

    @staticmethod
    def update_cart_item(item_id: int, update_data: dict):
        """Update cart item quantity with inventory reservation adjustments."""
        update_data = InputSanitizer.sanitize_json(update_data)
        if not current_user.is_authenticated:
            raise ServiceError("User must be authenticated", 401)
        user_id = current_user.id

        cart_item = CartItem.query.join(Cart).filter(Cart.user_id == user_id, CartItem.id == item_id).first()
        if not cart_item:
            raise NotFoundException("Cart item not found")
        
        if 'quantity' not in update_data:
            raise ValidationException("Quantity is required")
            
        try:
            new_quantity = int(update_data['quantity'])
        except (ValueError, TypeError):
            raise ValidationException("Quantity must be a valid number")

        if new_quantity <= 0:
            return CartService.remove_from_cart(item_id)

        old_quantity = cart_item.quantity
        quantity_diff = new_quantity - old_quantity

        if quantity_diff == 0:
            return cart_item.cart.to_dict()

        try:
            # Adjust inventory reservation
            if quantity_diff > 0:
                InventoryService.reserve_stock(cart_item.product_id, quantity_diff, user_id)
            elif quantity_diff < 0:
                InventoryService.release_stock(cart_item.product_id, -quantity_diff, user_id)

            # Update item quantity in cart
            cart_item.quantity = new_quantity
            db.session.commit()
            current_app.logger.info(f"Cart item updated: Item {item_id}, New quantity {new_quantity}")
            return cart_item.cart.to_dict()

        except ServiceError as e:
            db.session.rollback()
            current_app.logger.warning(f"Failed to update cart item {item_id} due to stock issue: {e.message}")
            raise e
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to update cart item {item_id}: {str(e)}", exc_info=True)
            raise ServiceError(f"Failed to update cart item: {str(e)}")

    @staticmethod
    def remove_from_cart(item_id: int):
        """Remove item from cart and release its inventory reservation."""
        if not current_user.is_authenticated:
            raise ServiceError("User must be authenticated", 401)
        user_id = current_user.id
        
        cart_item = CartItem.query.join(Cart).filter(Cart.user_id == user_id, CartItem.id == item_id).first()
        if not cart_item:
            raise NotFoundException("Cart item not found")

        try:
            quantity_to_release = cart_item.quantity
            product_id = cart_item.product_id
            cart = cart_item.cart

            db.session.delete(cart_item)
            db.session.commit()
            
            # Release the inventory reservation after successful removal from cart
            InventoryService.release_stock(product_id, quantity_to_release, user_id=user_id)
            
            current_app.logger.info(f"Cart item removed: Item {item_id}")
            return cart.to_dict()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to remove cart item {item_id}: {str(e)}", exc_info=True)
            raise ServiceError(f"Failed to remove cart item: {str(e)}")


    @staticmethod
    def clear_cart():
        """
        Clear all items from the current user's cart and release all reservations
        in a single atomic transaction.
        """
        if not current_user.is_authenticated:
            raise ServiceError("User must be authenticated", 401)
        user_id = current_user.id
        
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart or not cart.items:
            return # Cart is already empty, return a representation of an empty cart
            
        try:
            # Efficiently delete all cart items and reservations for the user in bulk.
            # This is wrapped in a single transaction.
            CartItem.query.filter_by(cart_id=cart.id).delete(synchronize_session=False)
            InventoryReservation.query.filter_by(user_id=user_id).delete(synchronize_session=False)
            
            db.session.commit()
            
            current_app.logger.info(f"Cart and all associated reservations cleared for user {user_id}")
            return cart.to_dict(cleared=True) # Assuming to_dict can handle this state
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to clear cart for user {user_id}: {str(e)}", exc_info=True)
            # The transaction is rolled back, so no reservations were released and no items were deleted.
            raise ServiceError(f"Failed to clear cart due to a database error.")
