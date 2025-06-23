from flask import Blueprint, request, jsonify
from backend.services.blog_service import BlogService
from backend.utils.sanitization import sanitize_input

blog_bp = Blueprint('blog_bp', __name__, url_prefix='/api/blog')

# READ all published blog posts (paginated and filterable)
@blog_bp.route('/posts', methods=['GET'])
def get_public_blog_posts():
    """
    Get a paginated list of all published blog posts.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category_slug = sanitize_input(request.args.get('category'))
        
        filters = {'status': 'published'}
        if category_slug:
            filters['category_slug'] = category_slug
            
        posts_pagination = BlogService.get_all_posts_paginated(page=page, per_page=per_page, filters=filters)
        
        return jsonify({
            "status": "success",
            "data": [p.to_dict_for_public() for p in posts_pagination.items],
            "total": posts_pagination.total,
            "pages": posts_pagination.pages,
            "current_page": posts_pagination.page
        }), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An error occurred while fetching blog posts."), 500

# READ a single published blog post by its slug
@blog_bp.route('/posts/<string:slug>', methods=['GET'])
def get_public_blog_post(slug):
    """
    Get a single published blog post by its slug.
    """
    clean_slug = sanitize_input(slug)
    post = BlogService.get_published_post_by_slug(clean_slug)
    if not post:
        return jsonify(status="error", message="Blog post not found"), 404
        
    return jsonify(status="success", data=post.to_dict_for_public()), 200

# READ all blog categories
@blog_bp.route('/categories', methods=['GET'])
def get_public_blog_categories():
    """
    Get a list of all blog categories that have at least one published post.
    """
    try:
        categories = BlogService.get_public_categories()
        return jsonify(status="success", data=[c.to_dict() for c in categories]), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An error occurred while fetching categories."), 500
