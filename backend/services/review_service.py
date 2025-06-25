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

```backend/services/blog_service.py`
```python
from backend.models import BlogPost, BlogCategory
from backend.database import db
from .exceptions import NotFoundException, ValidationException

class BlogService:
    # ... (create_post, update_post, etc. remain the same) ...

    @staticmethod
    def get_all_posts(include_deleted=False):
        query = BlogPost.query
        if include_deleted:
            query = query.with_deleted()
        return query.order_by(BlogPost.created_at.desc()).all()

    @staticmethod
    def soft_delete_post(post_id):
        post = BlogPost.query.get(post_id)
        if post:
            post.delete()
            return True
        return False

    @staticmethod
    def hard_delete_post(post_id):
        post = BlogPost.query.with_deleted().get(post_id)
        if post:
            post.hard_delete()
            return True
        return False

    @staticmethod
    def restore_post(post_id):
        post = BlogPost.query.with_deleted().get(post_id)
        if post:
            post.restore()
            return True
        return False

    # --- Blog Category Methods ---

    @staticmethod
    def get_all_categories(include_deleted=False):
        query = BlogCategory.query
        if include_deleted:
            query = query.with_deleted()
        return query.order_by(BlogCategory.name).all()
        
    @staticmethod
    def create_category(data):
        # ... implementation ...
        pass

    @staticmethod
    def soft_delete_category(category_id):
        category = BlogCategory.query.get(category_id)
        if category:
            category.delete()
            return True
        return False

    @staticmethod
    def hard_delete_category(category_id):
        category = BlogCategory.query.with_deleted().get(category_id)
        if category:
            category.hard_delete()
            return True
        return False

    @staticmethod
    def restore_category(category_id):
        category = BlogCategory.query.with_deleted().get(category_id)
        if category:
            category.restore()
            return True
        return False
