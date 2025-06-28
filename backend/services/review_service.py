from backend.models import Review
from backend.database import db
from .exceptions import NotFoundException

class ReviewService:
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
        if filters.get('include_deleted'):
            query = query.with_deleted()
        if filters.get('status'):
            query = query.filter(Review.status == filters['status'])
        # Add other filters as needed
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def approve_review(review_id):
        review = Review.query.get(review_id)
        if not review:
            raise NotFoundException("Review not found")
        review.status = 'approved'
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
