"""
This module defines the API endpoints for managing blog posts and categories
in the admin panel, using the declarative @api_resource_handler.
"""
from flask import Blueprint, request, g, jsonify
from ..models import BlogPost, BlogCategory
from ..schemas import BlogPostSchema, BlogCategorySchema
from ..utils.decorators import api_resource_handler, roles_required
from ..services.blog_service import BlogService

# --- Blueprint Setup ---
bp = Blueprint('blog_management', __name__, url_prefix='/api/admin/blog')

# --- Blog Post Endpoints ---

@bp.route('/posts', methods=['GET', 'POST'])
@bp.route('/posts/<int:post_id>', methods=['GET', 'PUT', 'DELETE'])
@roles_required('Admin', 'Manager', 'Editor')
@api_resource_handler(
    model=BlogPost,
    request_schema=BlogPostSchema,
    response_schema=BlogPostSchema,
    eager_loads=['author', 'category'],
    log_action=True,
    allow_hard_delete=False # Soft delete is the safe default
)
def handle_blog_posts(post_id=None, is_hard_delete=False):
    """Handles all CRUD operations for Blog Posts."""
    
    if request.method == 'GET' and post_id is None:
        # Handle paginated list view for all posts
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 15, type=int)
        paginated_posts = BlogService.get_all_posts_paginated(page=page, per_page=per_page)
        return jsonify({
            "data": BlogPostSchema(many=True).dump(paginated_posts.items),
            "total": paginated_posts.total,
            "pages": paginated_posts.pages,
            "current_page": paginated_posts.page
        })

    if request.method == 'GET':
        return g.target_object
    
    elif request.method == 'POST':
        # Automatically assign the current logged-in user as the author
        data = g.validated_data
        data['author_id'] = g.user.id
        return BlogService.create_article(data)
        
    elif request.method == 'PUT':
        return BlogService.update_article(post_id, g.validated_data)
        
    elif request.method == 'DELETE':
        if is_hard_delete:
            BlogService.hard_delete_article(post_id)
        else:
            BlogService.soft_delete_article(post_id)
        return None

# --- Blog Category Endpoints ---

@bp.route('/categories', methods=['GET', 'POST'])
@bp.route('/categories/<int:category_id>', methods=['GET', 'PUT', 'DELETE'])
@roles_required('Admin', 'Manager')
@api_resource_handler(
    model=BlogCategory,
    request_schema=BlogCategorySchema,
    response_schema=BlogCategorySchema,
    log_action=True,
    allow_hard_delete=False
)
def handle_blog_categories(category_id=None, is_hard_delete=False):
    """Handles all CRUD operations for Blog Categories."""

    if request.method == 'GET' and category_id is None:
        all_categories = BlogService.get_all_categories()
        return jsonify(BlogCategorySchema(many=True).dump(all_categories))

    if request.method == 'GET':
        return g.target_object
    elif request.method == 'POST':
        return BlogService.create_category(g.validated_data)
    elif request.method == 'PUT':
        return BlogService.update_category(category_id, g.validated_data)
    elif request.method == 'DELETE':
        # For categories, we might only ever want to soft delete
        # The service layer should contain the logic to prevent deletion if posts are attached.
        BlogService.delete_category(category_id)
        return None
