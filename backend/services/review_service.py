
from backend.database import db
from backend.models.product_models import Review, Product
from backend.models.user_models import User
from backend.services.exceptions import ValidationError, NotFoundError, PermissionError
from sqlalchemy import desc, func
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ReviewService:
    @staticmethod
    def get_all_reviews(page: int = 1, per_page: int = 20, status_filter: str = None) -> dict:
        """
        Get all reviews with pagination and filtering.
        """
        query = Review.query.join(User).join(Product)
        
        if status_filter:
            query = query.filter(Review.status == status_filter)
        
        reviews = query.order_by(desc(Review.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'reviews': [{
                'id': review.id,
                'rating': review.rating,
                'comment': review.comment,
                'status': review.status,
                'user': {
                    'id': review.user.id,
                    'name': f"{review.user.first_name} {review.user.last_name}"
                },
                'product': {
                    'id': review.product.id,
                    'name': review.product.name
                },
                'created_at': review.created_at.isoformat()
            } for review in reviews.items],
            'pagination': {
                'page': reviews.page,
                'pages': reviews.pages,
                'per_page': reviews.per_page,
                'total': reviews.total
            }
        }

    @staticmethod
    def update_review_status(review_id: int, status: str, admin_id: int) -> dict:
        """
        Update review status (approve/reject).
        """
        review = Review.query.get(review_id)
        if not review:
            raise NotFoundError(f"Review with ID {review_id} not found")
        
        valid_statuses = ['pending', 'approved', 'rejected']
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status. Must be one of: {valid_statuses}")
        
        old_status = review.status
        review.status = status
        review.moderated_by = admin_id
        review.moderated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log the status change
        logger.info(f"Review {review_id} status changed from {old_status} to {status} by admin {admin_id}")
        
        return {
            'id': review.id,
            'status': review.status,
            'moderated_at': review.moderated_at.isoformat()
        }

    @staticmethod
    def delete_review(review_id: int, admin_id: int) -> bool:
        """
        Delete a review (admin action).
        """
        review = Review.query.get(review_id)
        if not review:
            raise NotFoundError(f"Review with ID {review_id} not found")
        
        # Log before deletion
        logger.info(f"Review {review_id} deleted by admin {admin_id}")
        
        db.session.delete(review)
        db.session.commit()
        return True

    @staticmethod
    def get_review_statistics() -> dict:
        """
        Get review statistics for admin dashboard.
        """
        total_reviews = Review.query.count()
        pending_reviews = Review.query.filter_by(status='pending').count()
        approved_reviews = Review.query.filter_by(status='approved').count()
        rejected_reviews = Review.query.filter_by(status='rejected').count()
        
        avg_rating = db.session.query(func.avg(Review.rating)).filter_by(status='approved').scalar() or 0
        
        return {
            'total_reviews': total_reviews,
            'pending_reviews': pending_reviews,
            'approved_reviews': approved_reviews,
            'rejected_reviews': rejected_reviews,
            'average_rating': round(float(avg_rating), 2)
        }
