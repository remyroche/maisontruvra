# backend/blog/routes.py

from flask import Blueprint, jsonify
from backend.schemas import BlogPostSchema, BlogCategorySchema
from backend.services.blog_service import BlogService
from backend.services.exceptions import NotFoundException

blog_bp = Blueprint('blog_bp', __name__, url_prefix='/blog')
blog_service = BlogService()
blog_post_schema = BlogPostSchema()
blog_category_schema = BlogCategorySchema()


@blog_bp.route('/articles', methods=['GET'])
@cache.cached(timeout=21600)
def get_public_articles():
    """Public endpoint to get all published blog articles."""
    try:
        # In a real application, you might want a dedicated service method
        # like get_published_articles() that filters by is_published=True
        articles = blog_service.get_all_articles()
        published_articles = [
            article for article in articles if article.is_published]
        return jsonify(blog_post_schema.dump(published_articles, many=True))
    except Exception as e:
        # Add logging for unexpected errors
        return jsonify({"error": "An error occurred while fetching articles."}), 500


@blog_bp.route('/articles/<string:slug>', methods=['GET'])
@cache.cached(timeout=21600)
def get_public_article_by_slug(slug):
    """Public endpoint to get a single published blog article by slug."""
    try:
        article = blog_service.get_article_by_slug(slug)
        if not article.is_published:
            raise NotFoundException("Article not found.")
        return jsonify(blog_post_schema.dump(article))
    except NotFoundException:
        return jsonify({'error': 'Article not found'}), 404
    except Exception as e:
        # Add logging for unexpected errors
        return jsonify({"error": "An error occurred while fetching the article."}), 500


@blog_bp.route('/categories', methods=['GET'])
@cache.cached(timeout=21600)
def get_public_categories():
    """Public endpoint to get all blog categories."""
    try:
        categories = blog_service.get_all_categories()
        return jsonify(blog_category_schema.dump(categories, many=True))
    except Exception as e:
        # Add logging for unexpected errors
        return jsonify({"error": "An error occurred while fetching categories."}), 500
