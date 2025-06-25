# backend/services/blog_service.py

from sqlalchemy.orm import Session
from backend.database import db
from backend.models.blog_models import BlogPost, BlogCategory # Assuming BlogPost has a backref to BlogCategory named 'blog_posts'
from ..services.exceptions import NotFoundException, ValidationException
from backend.utils.input_sanitizer import InputSanitizer # Corrected: Use InputSanitizer
import bleach
import re
from .exceptions import ServiceError
from flask import current_app # Added: Import current_app

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
        for field in ['title', 'slug', 'meta_description', 'author', 'featured_image_url', 'excerpt', 'image_url']:
            if field in article_data:
                # Use InputSanitizer.sanitize_string and handle None
                sanitized_data[field] = InputSanitizer.sanitize_string(article_data[field]) if article_data[field] is not None else None

        # Sanitize HTML content with bleach, allowing a safe subset of HTML
        if 'content' in article_data:
            sanitized_data['content'] = bleach.clean(
                article_data['content'],
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRIBUTES,
                strip=True
            ) if article_data['content'] is not None else None
        else:
            sanitized_data['content'] = None # Ensure content is explicitly set to None if not provided

        # Pass through other fields without sanitization, but ensure they exist
        for field in ['category_id', 'is_published', 'author_id']:
            if field in article_data:
                sanitized_data[field] = article_data[field]
        
        # Ensure boolean fields are actually boolean
        if 'is_published' in sanitized_data:
            sanitized_data['is_published'] = bool(sanitized_data['is_published'])

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
            sanitized_data = self._sanitize_article_data(article_data)

            # Validate required fields for creation
            if not sanitized_data.get('title'):
                raise ValidationException("Article title is required.")
            
            # Generate slug if not provided
            if not sanitized_data.get('slug'):
                sanitized_data['slug'] = self._generate_slug(sanitized_data['title'])
            
            # Check for slug uniqueness
            if self.session.query(BlogPost).filter_by(slug=sanitized_data['slug']).first():
                raise ValidationException(f"Article with slug '{sanitized_data['slug']}' already exists.")

            new_post = BlogPost(
                title=sanitized_data['title'],
                slug=sanitized_data['slug'],
                content=sanitized_data.get('content'),
                excerpt=sanitized_data.get('excerpt'),
                image_url=sanitized_data.get('image_url'),
                author_id=sanitized_data.get('author_id'),
                category_id=sanitized_data.get('category_id'),
                is_published=sanitized_data.get('is_published', False) # Default to False if not provided
            )
            db.session.add(new_post)
            db.session.commit()
            return new_post
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error creating blog post: {e}", exc_info=True)
            raise ServiceError("Could not create blog post.")

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
        post = self.session.query(BlogPost).get(article_id) # Corrected: Use self.session and article_id
        if not post:
            raise NotFoundException("Blog post not found.") # Corrected: Use NotFoundException

        try:
            sanitized_data = self._sanitize_article_data(article_data)

            # Update fields only if they are provided in the sanitized data
            if 'title' in sanitized_data:
                post.title = sanitized_data['title']
            if 'slug' in sanitized_data:
                # Check for slug uniqueness if it's being changed
                if sanitized_data['slug'] != post.slug and \
                   self.session.query(BlogPost).filter_by(slug=sanitized_data['slug']).first():
                    raise ValidationException(f"Article with slug '{sanitized_data['slug']}' already exists.")
                post.slug = sanitized_data['slug']
            if 'content' in sanitized_data:
                post.content = sanitized_data['content']
            if 'excerpt' in sanitized_data:
                post.excerpt = sanitized_data['excerpt']
            if 'image_url' in sanitized_data:
                post.image_url = sanitized_data['image_url']
            if 'author_id' in sanitized_data:
                post.author_id = sanitized_data['author_id']
            if 'category_id' in sanitized_data:
                post.category_id = sanitized_data['category_id']
            if 'is_published' in sanitized_data:
                post.is_published = sanitized_data['is_published']
            
            self.session.commit() # Corrected: Use self.session
            return post
        except Exception as e:
            self.session.rollback() # Corrected: Use self.session
            current_app.logger.error(f"Database error updating blog post: {e}", exc_info=True)
            raise ServiceError("Could not update blog post.")

    def delete_article(self, article_id: int):
        """Deletes a blog post."""
        article = self.get_article_by_id(article_id)
        self.session.delete(article)
        self.session.commit()

    def create_category(self, category_data: dict) -> BlogCategory:
        """Creates a new blog category."""
        if 'name' not in category_data:
            raise ValidationException("Category name is required.")
        
        sanitized_name = InputSanitizer.sanitize_string(category_data['name'])
        
        # Check for uniqueness
        if self.session.query(BlogCategory).filter_by(name=sanitized_name).first():
            raise ValidationException(f"Category with name '{sanitized_name}' already exists.")

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
        
        sanitized_name = InputSanitizer.sanitize_string(category_data['name'])
        # Check for uniqueness if name is being changed
        if sanitized_name != category.name and \
           self.session.query(BlogCategory).filter_by(name=sanitized_name).first():
            raise ValidationException(f"Category with name '{sanitized_name}' already exists.")

        category.name = sanitized_name
        self.session.commit()
        return category

    def delete_category(self, category_id: int):
        """Deletes a blog category."""
        category = self.get_category_by_id(category_id)
        # Check if any blog posts are linked to this category
        if category.blog_posts.count() > 0: # Assuming a backref 'blog_posts' from BlogPost to BlogCategory
            raise ValidationException(f"Cannot delete category '{category.name}' because it has associated blog posts.")
        self.session.delete(category) # Corrected: Use self.session
        self.session.commit() # Corrected: Use self.session

        