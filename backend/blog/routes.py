# backend/blog/routes.py

from flask import Blueprint, jsonify, g
from backend.schemas import BlogPostSchema, BlogCategorySchema
from backend.services.blog_service import BlogService
from backend.services.exceptions import NotFoundException
from backend.extensions import cache
from backend.models.blog_models import BlogPost
from backend.utils.decorators import api_resource_handler

blog_bp = Blueprint("blog_bp", __name__, url_prefix="/blog")
blog_service = BlogService()
blog_post_schema = BlogPostSchema()
blog_category_schema = BlogCategorySchema()


@blog_bp.route("/articles", methods=["GET"])
@cache.cached(timeout=21600)
def get_public_articles():
    """Public endpoint to get all published blog articles."""
    try:
        # In a real application, you might want a dedicated service method
        # like get_published_articles() that filters by is_published=True
        articles = blog_service.get_all_articles()
        published_articles = [article for article in articles if article.is_published]
        return jsonify(blog_post_schema.dump(published_articles, many=True))
    except Exception:
        # Add logging for unexpected errors
        return jsonify({"error": "An error occurred while fetching articles."}), 500


@blog_bp.route("/articles/<string:slug>", methods=["GET"])
@api_resource_handler(
    model=BlogPost,
    response_schema=BlogPostSchema,
    ownership_exempt_roles=None,  # Public endpoint, no ownership checks
    eager_loads=["author", "category"],  # Eager load related data
    cache_timeout=21600,  # 6 hour cache for blog articles
    log_action=False,  # No need to log public blog views
    lookup_field="slug",  # Use slug for lookup instead of ID
)
def get_public_article_by_slug(slug):
    """Public endpoint to get a single published blog article by slug."""
    # Article is already fetched and validated by decorator
    article = g.target_object

    # Check if article is published
    if not article.is_published:
        raise NotFoundException("Article not found.")

    return article


@blog_bp.route("/categories", methods=["GET"])
@cache.cached(timeout=21600)
def get_public_categories():
    """Public endpoint to get all blog categories."""
    try:
        categories = blog_service.get_all_categories()
        return jsonify(blog_category_schema.dump(categories, many=True))
    except Exception:
        # Add logging for unexpected errors
        return jsonify({"error": "An error occurred while fetching categories."}), 500
