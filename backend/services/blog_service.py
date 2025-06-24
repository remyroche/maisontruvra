# backend/services/blog_service.py

from sqlalchemy.orm import Session
from ..models import db
from ..services.exceptions import NotFoundException, ValidationException
from ..utils.sanitization import sanitize_input
import bleach
import re
from ..models import BlogPost, BlogCategory
from .. import db
from .exceptions import ServiceError

ALLOWED_TAGS = ['p', 'a', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'br', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}

class BlogService:
    """
    Service layer for managing blog posts and categories.
    This service provides methods to interact with the blog-related
    database models, encapsulating the business logic away from the API endpoints.
    """

    def __init__(self, session: Session = db.session):
        """
        Initializes the BlogService with a database session.

        Args:
            session: The SQLAlchemy Session object.
        """
        self.session = session

    def _sanitize_article_data(self, article_data: dict) -> dict:
        """
        Sanitizes and validates article data.
        - Uses a basic sanitizer for most text fields.
        - Uses bleach for HTML content to prevent XSS attacks.
        """
        sanitized_data = {}
        # Fields to sanitize with a basic text sanitizer
        for field in ['title', 'slug', 'meta_description', 'author', 'featured_image_url']:
            if field in article_data and article_data[field]:
                sanitized_data[field] = sanitize_input(article_data[field])

        # Sanitize HTML content with bleach, allowing a safe subset of HTML
        if 'content' in article_data and article_data['content']:
            sanitized_data['content'] = bleach.clean(
                article_data['content'],
                tags=['p', 'b', 'i', 'u', 'a', 'h1', 'h2', 'h3', 'ul', 'ol', 'li', 'blockquote', 'pre', 'code', 'strong', 'em'],
                attributes={'a': ['href', 'title']},
                strip=True
            )

        # Pass through other fields without sanitization, but ensure they exist
        for field in ['category_id', 'is_published']:
            if field in article_data:
                sanitized_data[field] = article_data[field]

        return sanitized_data

    def _generate_slug(self, title: str) -> str:
        """Generates a URL-friendly slug from a title."""
        s = title.lower().strip()
        s = re.sub(r'[\s]+', '-', s)  # Replace spaces with -
        s = re.sub(r'[^\w\-]+', '', s) # Remove all non-word chars
        return s

    def create_article(self, article_data: dict) -> BlogPost:
        """
        Creates a new blog post after sanitizing its content.
        """
        try:
            # Sanitize the HTML content before creating the post
            sanitized_content = bleach.clean(
                data.get('content'),
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRIBUTES,
                strip=True  # Remove disallowed tags instead of escaping them
            )

            new_post = BlogPost(
                title=data.get('title'),
                slug=data.get('slug'),
                content=sanitized_content,  # Use the sanitized content
                excerpt=data.get('excerpt'),
                image_url=data.get('image_url'),
                author_id=data.get('author_id'),
                category_id=data.get('category_id')
            )
            db.session.add(new_post)
            db.session.commit()
            return new_post
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error creating blog post: {e}", exc_info=True)
            raise ServiceError("Could not create blog post.")
        return new_article

    def get_all_articles(self):
        """Retrieves all blog posts."""
        return self.session.query(BlogPost).order_by(BlogPost.created_at.desc()).all()

    def get_article_by_id(self, article_id: int) -> BlogPost:
        """
        Retrieves a single blog post by its ID.
        Raises NotFoundException if not found.
        """
        article = self.session.query(BlogPost).filter_by(id=article_id).first()
        if not article:
            raise NotFoundException(f"Article with id {article_id} not found.")
        return article

    def get_article_by_slug(self, slug: str) -> BlogPost:
        """
        Retrieves a single blog post by its slug.
        Raises NotFoundException if not found.
        """
        article = self.session.query(BlogPost).filter_by(slug=slug).first()
        if not article:
            raise NotFoundException(f"Article with slug '{slug}' not found.")
        return article

    def update_article(self, article_id: int, article_data: dict) -> BlogPost:
        """
        Updates an existing blog post after sanitizing its content.
        """
        post = BlogPost.query.get(post_id)
        if not post:
            raise ServiceError("Blog post not found.")

        try:
            if 'content' in data:
                # Sanitize the HTML content before updating
                post.content = bleach.clean(
                    data['content'],
                    tags=ALLOWED_TAGS,
                    attributes=ALLOWED_ATTRIBUTES,
                    strip=True
                )
            
            if 'title' in data:
                post.title = data['title']
            if 'slug' in data:
                post.slug = data['slug']
            
            db.session.commit()
            return post
        except Exception as e:
            db.session.rollback()
            print(f"Error updating blog post: {e}")
            raise ServiceError("Could not update blog post.")

        return article

    def delete_article(self, article_id: int):
        """Deletes a blog post."""
        article = self.get_article_by_id(article_id)
        self.session.delete(article)
        self.session.commit()

    def create_category(self, category_data: dict) -> BlogCategory:
        """Creates a new blog category."""
        if 'name' not in category_data:
            raise ValidationException("Category name is required.")
        sanitized_name = sanitize_input(category_data['name'])
        new_category = BlogCategory(name=sanitized_name)
        self.session.add(new_category)
        self.session.commit()
        return new_category

    def get_all_categories(self):
        """Retrieves all blog categories."""
        return self.session.query(BlogCategory).order_by(BlogCategory.name).all()

    def get_category_by_id(self, category_id: int) -> BlogCategory:
        """
        Retrieves a single blog category by its ID.
        Raises NotFoundException if not found.
        """
        category = self.session.query(BlogCategory).filter_by(id=category_id).first()
        if not category:
            raise NotFoundException(f"Category with id {category_id} not found.")
        return category

    def update_category(self, category_id: int, category_data: dict) -> BlogCategory:
        """Updates an existing blog category."""
        category = self.get_category_by_id(category_id)
        if 'name' not in category_data:
            raise ValidationException("Category name is required.")
        category.name = sanitize_input(category_data['name'])
        self.session.commit()
        return category

    def delete_category(self, category_id: int):
        """Deletes a blog category."""
        category = self.get_category_by_id(category_id)
        self.session.delete(category)
        self.session.commit()


        Args:
            category_id: The ID of the category to delete.

        Raises:
            NotFoundException: If the category is not found.
        """
        category = self.get_category_by_id(category_id)
        self.session.delete(category)
        self.session.commit()
