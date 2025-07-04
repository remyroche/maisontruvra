from backend.database import db
from ..models import Review, Product, User
from ..services.monitoring_service import MonitoringService
from ..services.audit_log_service import AuditLogService
from ..services.exceptions import NotFoundException, ValidationException, ServiceError
from ..utils.input_sanitizer import InputSanitizer


class ReviewService:
    """
    Handles business logic related to product reviews.
    """

    @staticmethod
    def get_reviews_for_product(product_id):
        """
        Retrieves all *approved* reviews for a specific product, ordered by most recent.
        This is for public display.
        """
        try:
            safe_product_id = InputSanitizer.sanitize_integer(product_id)
            product = Product.query.get(safe_product_id)
            if not product:
                raise NotFoundException("Product not found.")
            # Only fetch approved reviews for public display
            reviews = (
                Review.query.filter_by(product_id=safe_product_id, status="approved")
                .order_by(Review.created_at.desc())
                .all()
            )
            # Return the list of Review objects for the route to serialize
            return reviews
        except Exception as e:
            MonitoringService.log_error(
                f"Error getting reviews for product {product_id}: {str(e)}",
                "ReviewService",
                exc_info=True,
            )
            raise ServiceError(f"Failed to retrieve reviews: {str(e)}")

    @staticmethod
    def submit_review(user_id, product_id, rating, comment):
        """
        Allows a user to submit a new review for a product.
        Includes validation to ensure the user and product exist.
        """
        try:
            safe_user_id = InputSanitizer.sanitize_integer(user_id)
            safe_product_id = InputSanitizer.sanitize_integer(product_id)
            safe_rating = InputSanitizer.sanitize_integer(rating)
            safe_comment = InputSanitizer.sanitize_html(comment)

            # Validate rating
            if not 1 <= safe_rating <= 5:
                raise ValidationException("Rating must be between 1 and 5.")

            # Verify user and product exist
            user = User.query.get(safe_user_id)
            if not user:
                raise NotFoundException("User not found.")
            product = Product.query.get(safe_product_id)
            if not product:
                raise NotFoundException("Product not found.")

            # --- Optional: Check if user has purchased the product for a "Verified Purchase" tag ---
            # has_purchased = db.session.query(Order.id).join(OrderItem).filter(
            #     Order.user_id == safe_user_id,
            #     OrderItem.product_id == safe_product_id
            # ).first()
            # if not has_purchased:
            #     raise ValidationException("You can only review products you have purchased.")
            # ------------------------------------------------------------------------------------

            # Check if the user has already reviewed this product
            existing_review = Review.query.filter_by(
                user_id=safe_user_id, product_id=safe_product_id
            ).first()
            if existing_review:
                raise ValidationException("You have already reviewed this product.")

            new_review = Review(
                user_id=safe_user_id,
                product_id=safe_product_id,
                rating=safe_rating,
                comment=safe_comment,
            )

            db.session.add(new_review)
            db.session.commit()

            AuditLogService.log_action(
                user_id=safe_user_id,
                action="SUBMIT_REVIEW",
                details=f"User submitted a {safe_rating}-star review for product {safe_product_id}",
            )
            MonitoringService.log_info(
                f"User {safe_user_id} submitted review for product {safe_product_id}",
                "ReviewService",
            )

            return new_review.to_dict()

        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(
                f"Error submitting review for user {user_id}, product {product_id}: {str(e)}",
                "ReviewService",
                exc_info=True,
            )
            raise ServiceError(f"Failed to submit review: {str(e)}")

    @staticmethod
    def get_all_reviews(status_filter=None, include_deleted=False):
        query = Review.query
        if include_deleted:
            query = query.with_deleted()
        if status_filter:
            query = query.filter(Review.status == status_filter)
        return query.all()

    @staticmethod
    def get_all_reviews_paginated(page, per_page, filters):
        query = Review.query
        if filters.get("include_deleted"):
            query = query.with_deleted()
        if filters.get("status"):
            query = query.filter(Review.status == filters["status"])
        # Add other filters as needed
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def approve_review(review_id):
        review = Review.query.get(review_id)
        if not review:
            raise NotFoundException("Review not found")
        review.status = "approved"
        db.session.commit()
        return review

    @staticmethod
    def soft_delete_review(review_id):
        review = Review.query.get(review_id)
        if review:
            review.delete()
            return True
        return False

    @staticmethod
    def hard_delete_review(review_id):
        review = Review.query.with_deleted().get(review_id)
        if review:
            review.hard_delete()
            return True
        return False

    @staticmethod
    def restore_review(review_id):
        review = Review.query.with_deleted().get(review_id)
        if review:
            review.restore()
            return True
        return False
