"""
This module defines the API endpoints for managing blog posts and categories
in the admin panel, using the declarative @api_resource_handler.
"""
from flask import Blueprint, request, g, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.decorators import api_resource_handler, roles_required
from backend.models.blog_models import BlogPost, BlogCategory
from backend.schemas import BlogPostSchema, BlogCategorySchema
from backend.services.blog_service import BlogService
from backend.services.exceptions import ServiceException

# --- Blueprint Setup ---
bp = Blueprint('blog_management', __name__, url_prefix='/api/admin/blog')

# --- Blog Post Endpoints ---

@bp.route('/posts', methods=['GET'])
@jwt_required()
@roles_required('Admin', 'Manager', 'Editor')
def get_all_blog_posts():
    """Retrieves a paginated list of all blog posts."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 15, type=int)
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        
        paginated_posts = BlogService.get_all_posts_paginated(
            page=page, 
            per_page=per_page, 
            include_deleted=include_deleted
        )
        
        return jsonify({
            "data": BlogPostSchema(many=True).dump(paginated_posts.items),
            "total": paginated_posts.total,
            "pages": paginated_posts.pages,
            "current_page": paginated_posts.page
        })
    except ServiceException as e:
        return jsonify(e.to_dict()), e.status_code

@bp.route('/posts', methods=['POST'])
@jwt_required()
@roles_required('Admin', 'Manager', 'Editor')
@api_resource_handler(model=BlogPost, request_schema=BlogPostSchema, response_schema=BlogPostSchema, log_action=True)
def create_blog_post():
    """Creates a new blog post."""
    data = g.validated_data
    # Automatically assign the current logged-in user as the author
    data['author_id'] = get_jwt_identity()
    return BlogService.create_article(data)

@bp.route('/posts/<int:post_id>', methods=['GET'])
@jwt_required()
@roles_required('Admin', 'Manager', 'Editor')
@api_resource_handler(model=BlogPost, response_schema=BlogPostSchema, eager_loads=['author', 'category'])
def get_blog_post(post_id):
    """Retrieves a single blog post by its ID."""
    return g.target_object

@bp.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
@roles_required('Admin', 'Manager', 'Editor')
@api_resource_handler(model=BlogPost, request_schema=BlogPostSchema, response_schema=BlogPostSchema, log_action=True)
def update_blog_post(post_id):
    """Updates an existing blog post."""
    return BlogService.update_article(g.target_object, g.validated_data)

@bp.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
@roles_required('Admin', 'Manager', 'Editor')
@api_resource_handler(model=BlogPost, allow_hard_delete=True, log_action=True)
def delete_blog_post(post_id):
    """Deletes a blog post (soft by default)."""
    return None

@bp.route('/posts/<int:post_id>/restore', methods=['POST'])
@jwt_required()
@roles_required('Admin', 'Manager', 'Editor')
@api_resource_handler(model=BlogPost, response_schema=BlogPostSchema, log_action=True)
def restore_blog_post(post_id):
    """Restores a soft-deleted blog post."""
    return g.target_object

# --- Blog Category Endpoints ---

@bp.route('/categories', methods=['GET'])
@jwt_required()
@roles_required('Admin', 'Manager')
def get_all_blog_categories():
    """Retrieves a list of all blog categories."""
    try:
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        categories = BlogService.get_all_categories(include_deleted=include_deleted)
        return jsonify(BlogCategorySchema(many=True).dump(categories)), 200
    except ServiceException as e:
        return jsonify(e.to_dict()), e.status_code

@bp.route('/categories', methods=['POST'])
@jwt_required()
@roles_required('Admin', 'Manager')
@api_resource_handler(model=BlogCategory, request_schema=BlogCategorySchema, response_schema=BlogCategorySchema, log_action=True)
def create_blog_category():
    """Creates a new blog category."""
    return BlogService.create_category(g.validated_data)

@bp.route('/categories/<int:category_id>', methods=['GET'])
@jwt_required()
@roles_required('Admin', 'Manager')
@api_resource_handler(model=BlogCategory, response_schema=BlogCategorySchema)
def get_blog_category(category_id):
    """Retrieves a single blog category by its ID."""
    return g.target_object

@bp.route('/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
@roles_required('Admin', 'Manager')
@api_resource_handler(model=BlogCategory, request_schema=BlogCategorySchema, response_schema=BlogCategorySchema, log_action=True)
def update_blog_category(category_id):
    """Updates an existing blog category."""
    return BlogService.update_category(g.target_object, g.validated_data)

@bp.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
@roles_required('Admin', 'Manager')
@api_resource_handler(model=BlogCategory, allow_hard_delete=True, log_action=True)
def delete_blog_category(category_id):
    """Deletes a blog category (soft by default)."""
    return None

@bp.route('/categories/<int:category_id>/restore', methods=['POST'])
@jwt_required()
@roles_required('Admin', 'Manager')
@api_resource_handler(model=BlogCategory, response_schema=BlogCategorySchema, log_action=True)
def restore_blog_category(category_id):
    """Restores a soft-deleted blog category."""
    return g.target_object

