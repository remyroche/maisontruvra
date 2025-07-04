# backend/services/wishlist_service.py

from ..models import Wishlist, WishlistItem, Product, User, db
from ..services.monitoring_service import MonitoringService
from ..services.audit_log_service import AuditLogService
from ..services.exceptions import NotFoundException, ValidationException, ServiceError
from ..utils.input_sanitizer import InputSanitizer
from sqlalchemy.exc import IntegrityError


class WishlistService:
    """
    Handles business logic related to user wishlists.
    Combines a normalized data model with robust service logic.
    """

    @staticmethod
    def _get_or_create_wishlist(user_id):
        """
        Internal method to retrieve a user's wishlist. If it doesn't exist, it creates one.
        This ensures a user always has a wishlist container.
        """
        wishlist = Wishlist.query.filter_by(user_id=user_id).first()
        if not wishlist:
            # Verify user exists before creating a wishlist for them
            user = User.query.get(user_id)
            if not user:
                raise NotFoundException("User not found, cannot create wishlist.")
            wishlist = Wishlist(user_id=user_id)
            db.session.add(wishlist)
            db.session.commit()
        return wishlist

    @staticmethod
    def get_wishlist_items(user_id):
        """Get all wishlist items for a user."""
        try:
            safe_user_id = InputSanitizer.sanitize_integer(user_id)
            wishlist = WishlistService._get_or_create_wishlist(safe_user_id)

            # The relationship on the model will handle fetching the items.
            items = wishlist.items.order_by(WishlistItem.added_at.desc()).all()

            result = [item.to_dict() for item in items]

            MonitoringService.log_info(
                f"Retrieved {len(result)} wishlist items for user {safe_user_id}",
                "WishlistService",
            )
            return result
        except Exception as e:
            MonitoringService.log_error(
                f"Error getting wishlist items for user {user_id}: {str(e)}",
                "WishlistService",
                exc_info=True,
            )
            raise ServiceError(f"Failed to retrieve wishlist items: {str(e)}")

    @staticmethod
    def add_to_wishlist(user_id, product_id):
        """Add a product to a user's wishlist."""
        try:
            safe_user_id = InputSanitizer.sanitize_integer(user_id)
            safe_product_id = InputSanitizer.sanitize_integer(product_id)

            wishlist = WishlistService._get_or_create_wishlist(safe_user_id)

            # Verify product exists
            product = Product.query.get(safe_product_id)
            if not product:
                raise NotFoundException("Product not found")

            # Check if item already exists in wishlist using the relationship
            existing_item = wishlist.items.filter_by(product_id=safe_product_id).first()
            if existing_item:
                raise ValidationException("Product already in wishlist")

            # Create new wishlist item
            wishlist_item = WishlistItem(
                wishlist_id=wishlist.id, product_id=safe_product_id
            )
            db.session.add(wishlist_item)
            db.session.commit()

            AuditLogService.log_action(
                user_id=safe_user_id,
                action="ADD_TO_WISHLIST",
                details=f"Added product {safe_product_id} to wishlist",
            )
            MonitoringService.log_info(
                f"User {safe_user_id} added product {safe_product_id} to wishlist",
                "WishlistService",
            )
            return wishlist_item.to_dict()
        except IntegrityError:
            db.session.rollback()
            raise ValidationException("Product already in wishlist")
        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(
                f"Error adding product {product_id} to wishlist for user {user_id}: {str(e)}",
                "WishlistService",
                exc_info=True,
            )
            raise ServiceError(f"Failed to add product to wishlist: {str(e)}")

    @staticmethod
    def remove_from_wishlist(user_id, product_id):
        """Remove a product from a user's wishlist."""
        try:
            safe_user_id = InputSanitizer.sanitize_integer(user_id)
            safe_product_id = InputSanitizer.sanitize_integer(product_id)

            wishlist = WishlistService._get_or_create_wishlist(safe_user_id)

            # Find the wishlist item
            wishlist_item = wishlist.items.filter_by(product_id=safe_product_id).first()
            if not wishlist_item:
                raise NotFoundException("Product not found in wishlist")

            db.session.delete(wishlist_item)
            db.session.commit()

            AuditLogService.log_action(
                user_id=safe_user_id,
                action="REMOVE_FROM_WISHLIST",
                details=f"Removed product {safe_product_id} from wishlist",
            )
            MonitoringService.log_info(
                f"User {safe_user_id} removed product {safe_product_id} from wishlist",
                "WishlistService",
            )
            return True
        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(
                f"Error removing product {product_id} from wishlist for user {user_id}: {str(e)}",
                "WishlistService",
                exc_info=True,
            )
            raise ServiceError(f"Failed to remove product from wishlist: {str(e)}")

    @staticmethod
    def is_in_wishlist(user_id, product_id):
        """Check if a product is in a user's wishlist."""
        try:
            safe_user_id = InputSanitizer.sanitize_integer(user_id)
            safe_product_id = InputSanitizer.sanitize_integer(product_id)

            wishlist = Wishlist.query.filter_by(user_id=safe_user_id).first()
            if not wishlist:
                return False

            return wishlist.items.filter_by(product_id=safe_product_id).count() > 0
        except Exception as e:
            MonitoringService.log_error(
                f"Error checking wishlist for user {user_id}, product {product_id}: {str(e)}",
                "WishlistService",
            )
            return False
