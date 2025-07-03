from flask import current_app
from flask_login import current_user
from backend.database import db
from backend.models.product_models import Product, ProductVariant
from backend.models.inventory_models import InventoryReservation # Added: Import InventoryReservation
from .exceptions import ServiceError, ValidationException, NotFoundException
from .inventory_service import InventoryService
from .monitoring_service import MonitoringService
from backend.utils.input_sanitizer import InputSanitizer
from ..models import ExclusiveReward, Product, User
from backend.services.b2b_service import B2BService 
from decimal import Decimal
from .. import db
from ..models import Cart, CartItem, Product, User
from sqlalchemy.orm import joinedload
from backend.extensions import db
from .exceptions import ProductNotFoundError, InsufficientStockError
from ..models.enums import UserType

class CartService:
    def __init__(self, logger):
        self.logger = logger

    def get_cart_details(self, user_id):
        """
        Retrieves a user's cart and calculates prices, including B2B tier discounts.
        """
        user = db.session.query(User).options(
            joinedload(User.tier),
            joinedload(User.carts).joinedload(Cart.items).joinedload(CartItem.product)
        ).get(user_id)

        if not user:
            raise ProductNotFoundError("User not found.")

        cart = user.carts[0] if user.carts else None
        if not cart:
            # Create a cart if one doesn't exist
            cart = Cart(user_id=user.id)
            db.session.add(cart)
            db.session.commit()
            return {'cart': cart, 'items_details': [], 'subtotal': 0, 'total': 0, 'tier_discount': 0}

        items_details = []
        subtotal = Decimal('0.00')
        
        # Determine discount multiplier
        discount_multiplier = Decimal('1.0')
        tier_name = None
        if user.user_type == UserType.B2B and user.tier:
            tier = user.tier
            tier_name = tier.name
            discount_multiplier = Decimal('1') - (tier.discount_percentage / Decimal('100'))

        for item in cart.items:
            original_price = item.product.price
            # Apply tier discount if applicable
            final_price = (original_price * discount_multiplier).quantize(Decimal('0.01'))
            
            line_total = final_price * item.quantity
            items_details.append({
                'item_id': item.id,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'original_price': str(original_price),
                'final_price': str(final_price),
                'line_total': str(line_total)
            })
            subtotal += original_price * item.quantity

        total = sum(Decimal(i['line_total']) for i in items_details)
        tier_discount = subtotal - total

        return {
            'cart_id': cart.id,
            'items_details': items_details,
            'subtotal': str(subtotal),
            'tier_discount': str(tier_discount),
            'total': str(total),
            'tier_name': tier_name
        }

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
    def add_reward_to_cart(user_id, reward_id):
        """Adds a redeemed loyalty reward to the user's cart."""
        cart = CartService.get_cart(user_id)
        reward = ExclusiveReward.query.get(reward_id)

        if not reward or not reward.linked_product_id:
            raise ValidationException("This reward is not a physical product and cannot be added to the cart.")

        # Check if the reward is already in the cart to prevent duplicates
        existing_item = CartItem.query.filter_by(cart_id=cart.id, product_id=reward.linked_product_id, is_reward=True).first()
        if existing_item:
            raise ValidationException("This reward is already in your cart.")

        new_item = CartItem(
            cart_id=cart.id,
            product_id=reward.linked_product_id,
            quantity=1,
            is_reward=True # Mark this item as a free reward
        )
        db.session.add(new_item)
        db.session.commit()
        return cart
        
    @staticmethod
    def add_item_to_cart(self, user_id, product_id, quantity, custom_price=None):
        """
        Adds an item to a user's cart. Includes ownership check for exclusive products.
        """
        product = db.session.query(Product).get(product_id)
        if not product:
            raise ProductNotFoundError("Product not found.")

        # Security Check: Ensure user has permission to order this product
        if product.owner_id and product.owner_id != user_id:
            self.logger.warning(f"User {user_id} tried to add exclusive product {product_id} owned by {product.owner_id}.")
            raise PermissionError("This product is not available.")

        cart = db.session.query(Cart).filter_by(user_id=user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            db.session.add(cart)
            db.session.flush()

        # Check if item is already in cart
        cart_item = db.session.query(CartItem).filter_by(cart_id=cart.id, product_id=product_id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity,
                price=custom_price if custom_price is not None else product.price
            )
            db.session.add(cart_item)
        
        db.session.commit()
        self.logger.info(f"Added/updated product {product_id} in cart for user {user_id}.")
        return cart

        
    def update_cart_item(item_id: int, update_data: dict):
        """Update cart item quantity with inventory reservation adjustments."""
        update_data = InputSanitizer.sanitize_json(update_data)
        try:
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
            return cart_item.cart.to_dict()

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

    
    @staticmethod
    def remove_from_cart(user_id: int, product_id: int) -> Cart:
        item_id = "N/A"
        quantity_to_release = 0 # Default to 0 to prevent errors if cart_item is not found
        try:
            cart = Cart.query.filter_by(user_id=user_id).first()
            if cart:
                cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
                if cart_item:
                    db.session.delete(cart_item)
                    db.session.commit()
                    # Release the inventory reservation after successful removal from cart
                    InventoryService.release_stock(product_id, quantity_to_release, user_id=user_id)
                    
                    MonitoringService.log_info(
                        f"Cart item removed: Item {item_id}",
                        "CartService"
                    )
            return cart
        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(
                f"Failed to remove cart item {item_id}: {str(e)}",
                "CartService",
                exc_info=True
            )
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
            
            MonitoringService.log_info(
                f"Cart and all associated reservations cleared for user {user_id}",
                "CartService"
            )
            return cart.to_dict(cleared=True) # Assuming to_dict can handle this state
            
        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(
                f"Failed to clear cart for user {user_id}: {str(e)}",
                "CartService",
                exc_info=True
            )
            # The transaction is rolled back, so no reservations were released and no items were deleted.
            raise ServiceError(f"Failed to clear cart due to a database error.")
