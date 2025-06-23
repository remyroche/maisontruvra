
from backend.database import db
from backend.models.cart_models import CartItem
from backend.models.product_models import ProductVariant
from backend.models.user_models import User
from backend.services.exceptions import NotFoundException, ValidationException
from backend.utils.sanitization import sanitize_input
from flask_jwt_extended import get_jwt_identity
import logging

logger = logging.getLogger(__name__)

class CartService:
    @staticmethod
    def get_user_cart(user_id: int):
        """Get user's cart with N+1 optimization."""
        cart_items = CartItem.query.options(
            db.selectinload(CartItem.variant).selectinload(ProductVariant.product)
        ).filter_by(user_id=user_id).all()
        
        return [item.to_dict(context='full') for item in cart_items]
    
    @staticmethod
    def add_to_cart(cart_data: dict):
        """Add item to cart with proper validation."""
        cart_data = sanitize_input(cart_data)
        user_id = get_jwt_identity()
        
        if not user_id:
            raise ValidationException("User must be authenticated")
        
        # Validate required fields
        if not cart_data.get('variant_id') or not cart_data.get('quantity'):
            raise ValidationException("variant_id and quantity are required")
        
        variant_id = cart_data['variant_id']
        quantity = int(cart_data['quantity'])
        
        if quantity <= 0:
            raise ValidationException("Quantity must be positive")
        
        # Check if variant exists
        variant = ProductVariant.query.get(variant_id)
        if not variant:
            raise NotFoundException(f"Product variant with ID {variant_id} not found")
        
        # Check stock availability
        available_stock = variant.get_available_stock()
        if quantity > available_stock:
            raise ValidationException(f"Only {available_stock} items available in stock")
        
        try:
            # Check if item already in cart
            existing_item = CartItem.query.filter_by(
                user_id=user_id,
                variant_id=variant_id
            ).first()
            
            if existing_item:
                # Update quantity
                new_quantity = existing_item.quantity + quantity
                if new_quantity > available_stock:
                    raise ValidationException(f"Total quantity would exceed available stock ({available_stock})")
                existing_item.quantity = new_quantity
                cart_item = existing_item
            else:
                # Create new cart item
                cart_item = CartItem(
                    user_id=user_id,
                    variant_id=variant_id,
                    quantity=quantity
                )
                db.session.add(cart_item)
            
            db.session.commit()
            
            logger.info(f"Item added to cart: User {user_id}, Variant {variant_id}, Quantity {quantity}")
            return cart_item.to_dict(context='full')
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to add item to cart: {str(e)}")
            raise ValidationException(f"Failed to add item to cart: {str(e)}")
    
    @staticmethod
    def update_cart_item(item_id: int, update_data: dict):
        """Update cart item quantity."""
        update_data = sanitize_input(update_data)
        user_id = get_jwt_identity()
        
        cart_item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
        if not cart_item:
            raise NotFoundException("Cart item not found")
        
        if 'quantity' not in update_data:
            raise ValidationException("Quantity is required")
        
        quantity = int(update_data['quantity'])
        if quantity <= 0:
            # Remove item if quantity is 0 or negative
            return CartService.remove_from_cart(item_id)
        
        # Check stock availability
        available_stock = cart_item.variant.get_available_stock()
        if quantity > available_stock:
            raise ValidationException(f"Only {available_stock} items available in stock")
        
        try:
            cart_item.quantity = quantity
            db.session.commit()
            
            logger.info(f"Cart item updated: Item {item_id}, New quantity {quantity}")
            return cart_item.to_dict(context='full')
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update cart item {item_id}: {str(e)}")
            raise ValidationException(f"Failed to update cart item: {str(e)}")
    
    @staticmethod
    def remove_from_cart(item_id: int):
        """Remove item from cart."""
        user_id = get_jwt_identity()
        
        cart_item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
        if not cart_item:
            raise NotFoundException("Cart item not found")
        
        try:
            db.session.delete(cart_item)
            db.session.commit()
            
            logger.info(f"Cart item removed: Item {item_id}")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to remove cart item {item_id}: {str(e)}")
            raise ValidationException(f"Failed to remove cart item: {str(e)}")
    
    @staticmethod
    def clear_cart(user_id: int):
        """Clear all items from user's cart."""
        try:
            CartItem.query.filter_by(user_id=user_id).delete()
            db.session.commit()
            
            logger.info(f"Cart cleared for user {user_id}")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to clear cart for user {user_id}: {str(e)}")
            raise ValidationException(f"Failed to clear cart: {str(e)}")
    
    @staticmethod
    def get_cart_total(user_id: int):
        """Calculate cart total with tax."""
        cart_items = CartItem.query.options(
            db.selectinload(CartItem.variant)
        ).filter_by(user_id=user_id).all()
        
        subtotal = sum(item.quantity * item.variant.price for item in cart_items)
        tax_rate = 0.20  # 20% VAT
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount
        
        return {
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'total': total,
            'item_count': sum(item.quantity for item in cart_items)
        }
