# backend/services/blog_service.py

from sqlalchemy.orm import Session
from ..models import db
from ..models.blog_models import BlogPost, BlogCategory
from ..schemas import BlogPostSchema, BlogCategorySchema
from .exceptions import NotFoundException, ValidationException

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

    def create_article(self, article_data: dict) -> BlogPost:
        """
        Creates a new blog post.

        Args:
            article_data: A dictionary containing the data for the new article.

        Returns:
            The newly created BlogPost object.
        """
        # Add validation logic here if needed
        new_article = BlogPost(**article_data)
        self.session.add(new_article)
        self.session.commit()
        return new_article

    def get_all_articles(self):
        """
        Retrieves all blog posts.

        Returns:
            A list of all BlogPost objects.
        """
        return self.session.query(BlogPost).all()

    def get_article_by_id(self, article_id: int) -> BlogPost:
        """
        Retrieves a single blog post by its ID.

        Args:
            article_id: The ID of the blog post to retrieve.

        Returns:
            The BlogPost object if found.

        Raises:
            NotFoundException: If no blog post with the given ID is found.
        """
        article = self.session.query(BlogPost).filter_by(id=article_id).first()
        if not article:
            raise NotFoundException(f"Article with id {article_id} not found.")
        return article

    def update_article(self, article_id: int, article_data: dict) -> BlogPost:
        """
        Updates an existing blog post.

        Args:
            article_id: The ID of the blog post to update.
            article_data: A dictionary containing the updated data.

        Returns:
            The updated BlogPost object.

        Raises:
            NotFoundException: If the blog post is not found.
        """
        article = self.get_article_by_id(article_id)
        for key, value in article_data.items():
            setattr(article, key, value)
        self.session.commit()
        return article

    def delete_article(self, article_id: int):
        """
        Deletes a blog post.

        Args:
            article_id: The ID of the blog post to delete.

        Raises:
            NotFoundException: If the blog post is not found.
        """
        article = self.get_article_by_id(article_id)
        self.session.delete(article)
        self.session.commit()

    def create_category(self, category_data: dict) -> BlogCategory:
        """
        Creates a new blog category.

        Args:
            category_data: A dictionary containing the data for the new category.

        Returns:
            The newly created BlogCategory object.
        """
        new_category = BlogCategory(**category_data)
        self.session.add(new_category)
        self.session.commit()
        return new_category

    def get_all_categories(self):
        """
        Retrieves all blog categories.

        Returns:
            A list of all BlogCategory objects.
        """
        return self.session.query(BlogCategory).all()

    def get_category_by_id(self, category_id: int) -> BlogCategory:
        """
        Retrieves a single blog category by its ID.

        Args:
            category_id: The ID of the category to retrieve.

        Returns:
            The BlogCategory object if found.

        Raises:
            NotFoundException: If the category is not found.
        """
        category = self.session.query(BlogCategory).filter_by(id=category_id).first()
        if not category:
            raise NotFoundException(f"Category with id {category_id} not found.")
        return category

    def update_category(self, category_id: int, category_data: dict) -> BlogCategory:
        """
        Updates an existing blog category.

        Args:
            category_id: The ID of the category to update.
            category_data: A dictionary containing the updated data.

        Returns:
            The updated BlogCategory object.

        Raises:
            NotFoundException: If the category is not found.
        """
        category = self.get_category_by_id(category_id)
        for key, value in category_data.items():
            setattr(category, key, value)
        self.session.commit()
        return category

    def delete_category(self, category_id: int):
        """
        Deletes a blog category.

        Args:
            category_id: The ID of the category to delete.

        Raises:
            NotFoundException: If the category is not found.
        """
        category = self.get_category_by_id(category_id)
        self.session.delete(category)
        self.session.commit()
