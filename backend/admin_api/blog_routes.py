# backend/admin_api/blog_routes.py

from flask import Blueprint, request, jsonify
from backend.schemas import BlogPostSchema, BlogCategorySchema
from flask_jwt_extended import jwt_required
from ..utils.decorators import admin_required, staff_required, roles_required, permissions_required
from ..utils.decorators import log_admin_action
from backend.services.blog_service import BlogService
from backend.services.exceptions import NotFoundException, ValidationException

admin_blog_bp = Blueprint('admin_blog_bp', __name__, url_prefix='/admin/blog')
blog_service = BlogService()
blog_post_schema = BlogPostSchema()
blog_category_schema = BlogCategorySchema()

@admin_blog_bp.route("/articles", methods=["POST"])
@jwt_required()
@log_admin_action
@roles_required ('Admin', 'Editor', 'Manager')
@admin_required
def create_article():
    """Admin endpoint to create a new blog article."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    try:
        new_article = blog_service.create_article(data)
        return jsonify(blog_post_schema.dump(new_article)), 201
    except ValidationException as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Add logging for unexpected errors
        return jsonify({"error": "An unexpected error occurred"}), 500

@admin_blog_bp.route("/articles", methods=["GET"])
@jwt_required()
@log_admin_action
@roles_required ('Admin', 'Editor', 'Manager')
@admin_required
def get_articles():
    """Admin endpoint to get all blog articles."""
    articles = blog_service.get_all_articles()
    return jsonify(blog_post_schema.dump(articles, many=True)), 200

@admin_blog_bp.route("/articles/<int:article_id>", methods=["GET"])
@jwt_required()
@log_admin_action
@roles_required ('Admin', 'Editor', 'Manager')
@admin_required
def get_article(article_id):
    """Admin endpoint to get a single blog article by ID."""
    try:
        article = blog_service.get_article_by_id(article_id)
        return jsonify(blog_post_schema.dump(article)), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404

@admin_blog_bp.route("/articles/<int:article_id>", methods=["PUT"])
@jwt_required()
@log_admin_action
@roles_required ('Admin', 'Editor', 'Manager')
@admin_required
def update_article(article_id):
    """Admin endpoint to update a blog article."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    try:
        updated_article = blog_service.update_article(article_id, data)
        return jsonify(blog_post_schema.dump(updated_article)), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except ValidationException as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Add logging for unexpected errors
        return jsonify({"error": "An unexpected error occurred"}), 500

@admin_blog_bp.route("/articles/<int:article_id>", methods=["DELETE"])
@jwt_required()
@log_admin_action
@roles_required ('Admin', 'Editor', 'Manager')
@admin_required
def delete_article(article_id):
    """Admin endpoint to delete a blog article."""
    try:
        blog_service.delete_article(article_id)
        return jsonify({"message": "Article deleted successfully"}), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404

@admin_blog_bp.route("/categories", methods=["POST"])
@jwt_required()
@log_admin_action
@roles_required ('Admin', 'Editor', 'Manager')
@admin_required
def create_category():
    """Admin endpoint to create a new blog category."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Invalid data, 'name' is required"}), 400
    try:
        new_category = blog_service.create_category(data)
        return jsonify(blog_category_schema.dump(new_category)), 201
    except ValidationException as e:
        return jsonify({"error": str(e)}), 400

@admin_blog_bp.route("/categories", methods=["GET"])
@jwt_required()
@log_admin_action
@roles_required ('Admin', 'Editor', 'Manager')
@admin_required
def get_categories():
    """Admin endpoint to get all blog categories."""
    categories = blog_service.get_all_categories()
    return jsonify(blog_category_schema.dump(categories, many=True)), 200

@admin_blog_bp.route("/categories/<int:category_id>", methods=["PUT"])
@jwt_required()
@log_admin_action
@roles_required ('Admin', 'Editor', 'Manager')
@admin_required
def update_category(category_id):
    """Admin endpoint to update a blog category."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Invalid data, 'name' is required"}), 400
    try:
        updated_category = blog_service.update_category(category_id, data)
        return jsonify(blog_category_schema.dump(updated_category)), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except ValidationException as e:
        return jsonify({"error": str(e)}), 400

@admin_blog_bp.route("/categories/<int:category_id>", methods=["DELETE"])
@jwt_required()
@log_admin_action
@roles_required ('Admin', 'Editor', 'Manager')
@admin_required
def delete_category(category_id):
    """Admin endpoint to delete a blog category."""
    try:
        blog_service.delete_category(category_id)
        return jsonify({"message": "Category deleted successfully"}), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
