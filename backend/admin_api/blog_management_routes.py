from flask import Blueprint, request, jsonify
from backend.services.blog_service import BlogService
from backend.auth.permissions import admin_required, roles_required
from ..utils.decorators import log_admin_action

blog_management_bp = Blueprint('blog_management_bp', __name__, url_prefix='/api/admin/blog')

# Blog Post Routes
@blog_management_bp.route('/posts', methods=['GET'])
@log_admin_action
@roles_required('Admin', 'Manager', 'Editor')
def get_posts():
    include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
    posts = BlogService.get_all_posts(include_deleted=include_deleted)
    return jsonify([post.to_dict() for post in posts])

@blog_management_bp.route('/posts', methods=['POST'])
@log_admin_action
@roles_required('Admin', 'Manager', 'Editor')
def create_post():
    data = request.get_json()
    post = BlogService.create_post(data)
    return jsonify(post.to_dict()), 201

@blog_management_bp.route('/posts/<int:post_id>', methods=['PUT'])
@log_admin_action
@roles_required('Admin', 'Manager', 'Editor')
def update_post(post_id):
    data = request.get_json()
    post = BlogService.update_post(post_id, data)
    if not post:
        return jsonify({"error": "Blog post not found"}), 404
    return jsonify(post.to_dict())

@blog_management_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@log_admin_action
@roles_required('Admin', 'Manager', 'Editor')
def delete_post(post_id):
    hard_delete = request.args.get('hard', 'false').lower() == 'true'
    if hard_delete:
        if BlogService.hard_delete_post(post_id):
            return jsonify({"message": "Blog post permanently deleted"})
    else:
        if BlogService.soft_delete_post(post_id):
            return jsonify({"message": "Blog post soft-deleted"})
    return jsonify({"error": "Blog post not found"}), 404

@blog_management_bp.route('/posts/<int:post_id>/restore', methods=['PUT'])
@log_admin_action
@roles_required('Admin', 'Manager', 'Editor')
def restore_post(post_id):
    if BlogService.restore_post(post_id):
        return jsonify({"message": "Blog post restored"})
    return jsonify({"error": "Blog post not found"}), 404

# Blog Category Routes
@blog_management_bp.route('/categories', methods=['GET'])
@log_admin_action
@roles_required('Admin', 'Manager', 'Editor')
def get_categories():
    include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
    categories = BlogService.get_all_categories(include_deleted=include_deleted)
    return jsonify([category.to_dict() for category in categories])

@blog_management_bp.route('/categories', methods=['POST'])
@log_admin_action
@roles_required('Admin', 'Manager', 'Editor')
def create_category():
    data = request.get_json()
    category = BlogService.create_category(data)
    return jsonify(category.to_dict()), 201

@blog_management_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@log_admin_action
@roles_required('Admin', 'Manager', 'Editor')
def delete_category(category_id):
    hard_delete = request.args.get('hard', 'false').lower() == 'true'
    if hard_delete:
        if BlogService.hard_delete_category(category_id):
            return jsonify({"message": "Blog category permanently deleted"})
    else:
        if BlogService.soft_delete_category(category_id):
            return jsonify({"message": "Blog category soft-deleted"})
    return jsonify({"error": "Blog category not found"}), 404

@blog_management_bp.route('/categories/<int:category_id>/restore', methods=['PUT'])
@log_admin_action
@roles_required('Admin', 'Manager', 'Editor')
def restore_category(category_id):
    if BlogService.restore_category(category_id):
        return jsonify({"message": "Blog category restored"})
    return jsonify({"error": "Blog category not found"}), 404
