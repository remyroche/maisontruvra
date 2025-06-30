from flask import current_app
from flask_login import current_user
from backend.models import db, Cart, CartItem, Product, User
from backend.services.exceptions import NotFoundException, ServiceError, ValidationException
from backend.services.b2b_service import B2BService
from backend.services.inventory_service import InventoryService
from backend.services.monitoring_service import MonitoringService
from backend.utils.input_sanitizer import InputSanitizer
from backend.models.enums import UserType
from decimal import Decimal

class CartService:
    @staticmethod
    def get_cart(user_id: int) -> dict:
        """
        Retrieves the user's cart. If the user is B2B, it applies tiered pricing.
        """
        user = db.session.get(User, user_id)
        if not user:
            raise NotFoundException("User not found")

        if user.user_type == UserType.B2B:
            return B2BService.get_cart_with_b2b_pricing(user_id)

        # B2C cart logic
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            # Optionally create a cart if it doesn't exist
            cart = Cart(user_id=user_id)
            db.session.add(cart)
            db.session.commit()

        subtotal = sum(item.product.price * item.quantity for item in cart.items)
        
        return {
            'cart': cart,
            'items_details': [{
                'item': item,
                'original_price': item.product.price,
                'discounted_price': item.product.price, # No discount for B2C from tier
                'line_total': item.product.price * item.quantity
            } for item in cart.items],
            'subtotal': subtotal,
            'discount_applied': Decimal('0.00'),
            'total': subtotal,
            'tier_name': None
        }

    @staticmethod
    def add_to_cart(user_id: int, product_id: int, quantity: int) -> Cart:
        """Adds a product to the cart and reserves stock."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")

        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            db.session.add(cart)
            db.session.commit() # Commit to get cart.id
        
        product = Product.query.get_or_404(product_id)
        
        cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        
        try:
            # Reserve stock before making changes
            InventoryService.reserve_stock(product_id, quantity, user_id)

            if cart_item:
                cart_item.quantity += quantity
            else:
                price = product.price 
                cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity, price=price)
                db.session.add(cart_item)
            
            db.session.commit()
        except ServiceError as e:
            db.session.rollback()
            MonitoringService.log_warning(f"Failed to add to cart due to stock issue: {e.message}", "CartService")
            raise e
        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(f"Failed to add item to cart: {str(e)}", "CartService", exc_info=True)
            raise ServiceError(f"Could not add item to cart: {str(e)}")


        return cart

    @staticmethod
    def remove_from_cart(user_id: int, item_id: int) -> Cart:
        """Removes an item from the cart by its ID and releases inventory."""
        cart_item = CartItem.query.join(Cart).filter(Cart.user_id == user_id, CartItem.id == item_id).first()
        if not cart_item:
            raise NotFoundException("Cart item not found")

        cart = cart_item.cart
        
        try:
            # Release the reserved stock
            InventoryService.release_stock(cart_item.product_id, cart_item.quantity, user_id)
            
            db.session.delete(cart_item)
            db.session.commit()
            
            MonitoringService.log_info(f"Cart item removed: Item {item_id}", "CartService")
        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(f"Failed to remove cart item {item_id}: {str(e)}", "CartService", exc_info=True)
            raise ServiceError(f"Failed to remove cart item: {str(e)}")

        return cart

    @staticmethod
    def update_cart_item(user_id: int, item_id: int, update_data: dict) -> Cart:
        """Update cart item quantity with inventory reservation adjustments."""
        update_data = InputSanitizer.sanitize_json(update_data)
        
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
            return CartService.remove_from_cart(user_id, item_id)

        old_quantity = cart_item.quantity
        quantity_diff = new_quantity - old_quantity

        if quantity_diff == 0:
            return cart_item.cart

        try:
            # Adjust inventory reservation
            if quantity_diff > 0:
                InventoryService.reserve_stock(cart_item.product_id, quantity_diff, user_id)
            elif quantity_diff < 0:
                InventoryService.release_stock(cart_item.product_id, -quantity_diff, user_id)

            # Update item quantity in cart
            cart_item.quantity = new_quantity
            db.session.commit()
            MonitoringService.log_info(
                f"Cart item updated: Item {item_id}, New quantity {new_quantity}",
                "CartService"
            )
            return cart_item.cart

        except ServiceError as e:
            db.session.rollback()
            MonitoringService.log_warning(
                f"Failed to update cart item {item_id} due to stock issue: {e.message}",
                "CartService"
            )
            raise e
        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(
                f"Failed to update cart item {item_id}: {str(e)}",
                "CartService",
                exc_info=True
            )
            raise ServiceError(f"Failed to update cart item: {str(e)}")
