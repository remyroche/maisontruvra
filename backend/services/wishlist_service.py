from backend.database import db
from backend.models.user_models import User
from backend.models.product_models import Product
from backend.services.monitoring_service import MonitoringService
from backend.services.exceptions import NotFoundException, ValidationException, ServiceError
from backend.utils.input_sanitizer import InputSanitizer
from backend.services.audit_log_service import AuditLogService
from flask import current_app
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.exc import IntegrityError


class WishlistItem(db.Model):
    """Wishlist item model - this should ideally be in models/wishlist_models.py"""
    __tablename__ = 'wishlist_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationships
    user = db.relationship('User', backref='wishlist_items')
    product = db.relationship('Product', backref='wishlist_items')
    
    # Unique constraint to prevent duplicate wishlist items
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_user_product_wishlist'),)


class WishlistService:
    """Service for managing user wishlists"""
    
    @staticmethod
    def get_wishlist_items(user_id):
        """Get all wishlist items for a user"""
        try:
            user_id = InputSanitizer.InputSanitizer.sanitize_input(user_id)
            
            # Verify user exists
            user = User.query.get(user_id)
            if not user:
                raise NotFoundException("User not found")
            
            wishlist_items = WishlistItem.query.filter_by(user_id=user_id).all()
            
            result = []
            for item in wishlist_items:
                result.append({
                    'id': item.id,
                    'product_id': item.product_id,
                    'product': {
                        'id': item.product.id,
                        'name': item.product.name,
                        'price': float(item.product.price) if item.product.price else 0,
                        'image_url': item.product.image_url,
                        'description': item.product.description
                    },
                    'created_at': item.created_at.isoformat() if item.created_at else None
                })
            
            MonitoringService.log_info(
                f"Retrieved {len(result)} wishlist items for user {user_id}",
                "WishlistService"
            )
            return result
            
        except Exception as e:
            MonitoringService.log_error(
                f"Error getting wishlist items for user {user_id}: {str(e)}",
                "WishlistService",
                exc_info=True
            )
            raise ServiceError(f"Failed to retrieve wishlist items: {str(e)}")
    
    @staticmethod
    def add_to_wishlist(user_id, product_id):
        """Add a product to user's wishlist"""
        try:
            user_id = InputSanitizer.InputSanitizer.sanitize_input(user_id)
            product_id = InputSanitizer.InputSanitizer.sanitize_input(product_id)
            
            # Verify user exists
            user = User.query.get(user_id)
            if not user:
                raise NotFoundException("User not found")
            
            # Verify product exists
            product = Product.query.get(product_id)
            if not product:
                raise NotFoundException("Product not found")
            
            # Check if item already exists in wishlist
            existing_item = WishlistItem.query.filter_by(
                user_id=user_id, 
                product_id=product_id
            ).first()
            
            if existing_item:
                raise ValidationException("Product already in wishlist")
            
            # Create new wishlist item
            wishlist_item = WishlistItem(
                user_id=user_id,
                product_id=product_id
            )
            
            db.session.add(wishlist_item)
            db.session.commit()
            
            # Log the action
            AuditLogService.log_action(
                user_id=user_id,
                action="ADD_TO_WISHLIST",
                resource_type="WISHLIST",
                resource_id=wishlist_item.id,
                details=f"Added product {product_id} to wishlist"
            )
            
            MonitoringService.log_info(
                f"User {user_id} added product {product_id} to wishlist",
                "WishlistService"
            )
            
            return {
                'id': wishlist_item.id,
                'product_id': product_id,
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': float(product.price) if product.price else 0,
                    'image_url': product.image_url,
                    'description': product.description
                },
                'created_at': wishlist_item.created_at.isoformat() if wishlist_item.created_at else None
            }
            
        except IntegrityError:
            db.session.rollback()
            raise ValidationException("Product already in wishlist")
        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(f"Error adding product {product_id} to wishlist for user {user_id}: {str(e)}")
            raise ServiceError(f"Failed to add product to wishlist: {str(e)}")
    
    @staticmethod
    def remove_from_wishlist(user_id, product_id):
        """Remove a product from user's wishlist"""
        try:
            user_id = InputSanitizer.InputSanitizer.sanitize_input(user_id)
            product_id = InputSanitizer.InputSanitizer.sanitize_input(product_id)
            
            # Find the wishlist item
            wishlist_item = WishlistItem.query.filter_by(
                user_id=user_id,
                product_id=product_id
            ).first()
            
            if not wishlist_item:
                raise NotFoundException("Product not found in wishlist")
            
            # Remove the item
            db.session.delete(wishlist_item)
            db.session.commit()
            
            # Log the action
            AuditLogService.log_action(
                user_id=user_id,
                action="REMOVE_FROM_WISHLIST",
                resource_type="WISHLIST",
                resource_id=wishlist_item.id,
                details=f"Removed product {product_id} from wishlist"
            )
            
            MonitoringService.log_info(
                f"User {user_id} removed product {product_id} from wishlist",
                "WishlistService"
            )
            return True
            
        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(f"Error removing product {product_id} from wishlist for user {user_id}: {str(e)}")
            raise ServiceError(f"Failed to remove product from wishlist: {str(e)}")
    
    @staticmethod
    def clear_wishlist(user_id):
        """Clear all items from user's wishlist"""
        try:
            user_id = InputSanitizer.InputSanitizer.sanitize_input(user_id)
            
            # Verify user exists
            user = User.query.get(user_id)
            if not user:
                raise NotFoundException("User not found")
            
            # Remove all wishlist items for the user
            deleted_count = WishlistItem.query.filter_by(user_id=user_id).delete()
            db.session.commit()
            
            # Log the action
            AuditLogService.log_action(
                user_id=user_id,
                action="CLEAR_WISHLIST",
                resource_type="WISHLIST",
                resource_id=None,
                details=f"Cleared {deleted_count} items from wishlist"
            )
            
            MonitoringService.log_info(
                f"User {user_id} cleared {deleted_count} items from wishlist",
                "WishlistService"
            )
            return deleted_count
            
        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(f"Error clearing wishlist for user {user_id}: {str(e)}")
            raise ServiceError(f"Failed to clear wishlist: {str(e)}")
    
    @staticmethod
    def is_in_wishlist(user_id, product_id):
        """Check if a product is in user's wishlist"""
        try:
            user_id = InputSanitizer.InputSanitizer.sanitize_input(user_id)
            product_id = InputSanitizer.InputSanitizer.sanitize_input(product_id)
            
            wishlist_item = WishlistItem.query.filter_by(
                user_id=user_id,
                product_id=product_id
            ).first()
            
            return wishlist_item is not None
            
        except Exception as e:
            MonitoringService.log_error(f"Error checking if product {product_id} is in wishlist for user {user_id}: {str(e)}")
            return False
    
    @staticmethod
    def get_wishlist_count(user_id):
        """Get the count of items in user's wishlist"""
        try:
            user_id = InputSanitizer.InputSanitizer.sanitize_input(user_id)
            
            count = WishlistItem.query.filter_by(user_id=user_id).count()
            return count
            
        except Exception as e:
            MonitoringService.log_error(f"Error getting wishlist count for user {user_id}: {str(e)}")
            return 0