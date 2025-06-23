from flask import Blueprint, request, jsonify
from backend.services.blog_service import BlogService # Assumed service
from backend.utils.sanitization import sanitize_input
from backend.auth.permissions import permissions_required

blog_management_bp = Blueprint('blog_management_bp', __name__, url_prefix='/admin/blog')

# --- Blog Post Routes ---

# CREATE a new blog post
@blog_management_bp.route('/posts', methods=['POST'])
@permissions_required('MANAGE_BLOG')
def create_blog_post():
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Invalid JSON"), 400
    
    required_fields = ['title', 'content', 'author_id', 'category_id']
    if not all(field in data for field in required_fields):
        return jsonify(status="error", message="Missing required fields"), 400

    sanitized_data = sanitize_input(data)
    try:
        new_post = BlogService.create_post(sanitized_data)
        return jsonify(status="success", data=new_post.to_dict()), 201
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        return jsonify(status="error", message="Failed to create blog post."), 500

# READ all blog posts (paginated)
@blog_management_bp.route('/posts', methods=['GET'])
@permissions_required('MANAGE_BLOG')
def get_blog_posts():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 15, type=int)
        posts_pagination = BlogService.get_all_posts_paginated(page=page, per_page=per_page)
        return jsonify({
            "status": "success",
            "data": [p.to_dict() for p in posts_pagination.items],
            "total": posts_pagination.total,
            "pages": posts_pagination.pages,
            "current_page": posts_pagination.page
        }), 200
    except Exception as e:
        return jsonify(status="error", message="Failed to retrieve blog posts."), 500

# READ a single blog post
@blog_management_bp.route('/posts/<int:post_id>', methods=['GET'])
@permissions_required('MANAGE_BLOG')
def get_blog_post(post_id):
    post = BlogService.get_post_by_id(post_id)
    if not post:
        return jsonify(status="error", message="Blog post not found"), 404
    return jsonify(status="success", data=post.to_dict()), 200

# UPDATE a blog post
@blog_management_bp.route('/posts/<int:post_id>', methods=['PUT'])
@permissions_required('MANAGE_BLOG')
def update_blog_post(post_id):
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Invalid JSON"), 400
    if not BlogService.get_post_by_id(post_id):
        return jsonify(status="error", message="Blog post not found"), 404
        
    sanitized_data = sanitize_input(data)
    try:
        updated_post = BlogService.update_post(post_id, sanitized_data)
        return jsonify(status="success", data=updated_post.to_dict()), 200
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        return jsonify(status="error", message="Failed to update blog post."), 500

# DELETE a blog post
@blog_management_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@permissions_required('MANAGE_BLOG')
def delete_blog_post(post_id):
    if not BlogService.get_post_by_id(post_id):
        return jsonify(status="error", message="Blog post not found"), 404
    try:
        BlogService.delete_post(post_id)
        return jsonify(status="success", message="Blog post deleted successfully"), 200
    except Exception as e:
        return jsonify(status="error", message="Failed to delete blog post."), 500

# --- Blog Category Routes ---

# CREATE a new category
@blog_management_bp.route('/categories', methods=['POST'])
@permissions_required('MANAGE_BLOG')
def create_blog_category():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify(status="error", message="Invalid JSON or missing 'name' field"), 400
    
    sanitized_name = sanitize_input(data['name'])
    try:
        new_category = BlogService.create_category({'name': sanitized_name, 'description': sanitize_input(data.get('description'))})
        return jsonify(status="success", data=new_category.to_dict()), 201
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 409 # 409 Conflict if category exists
    except Exception as e:
        return jsonify(status="error", message="Failed to create category."), 500

# READ all categories
@blog_management_bp.route('/categories', methods=['GET'])
@permissions_required('MANAGE_BLOG')
def get_blog_categories():
    try:
        categories = BlogService.get_all_categories()
        return jsonify(status="success", data=[c.to_dict() for c in categories]), 200
    except Exception as e:
        return jsonify(status="error", message="Failed to retrieve categories."), 500

# UPDATE a category
@blog_management_bp.route('/categories/<int:category_id>', methods=['PUT'])
@permissions_required('MANAGE_BLOG')
def update_blog_category(category_id):
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Invalid JSON"), 400
    if not BlogService.get_category_by_id(category_id):
        return jsonify(status="error", message="Category not found"), 404

    sanitized_data = sanitize_input(data)
    try:
        updated_category = BlogService.update_category(category_id, sanitized_data)
        return jsonify(status="success", data=updated_category.to_dict()), 200
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        return jsonify(status="error", message="Failed to update category."), 500

# DELETE a category
@blog_management_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@permissions_required('MANAGE_BLOG')
def delete_blog_category(category_id):
    if not BlogService.get_category_by_id(category_id):
        return jsonify(status="error", message="Category not found"), 404
    try:
        BlogService.delete_category(category_id)
        return jsonify(status="success", message="Category deleted successfully"), 200
    except Exception as e:
        # Proper logging should be implemented here
        return jsonify(status="error", message=str(e)), 500
