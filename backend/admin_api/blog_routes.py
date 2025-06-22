from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from backend.models.blog_models import BlogPost, BlogCategory
from backend.extensions import db
from backend.auth.permissions import permission_required, Permission
from backend.utils.sanitization import sanitize_input

blog_bp = Blueprint('admin_blog_bp', __name__, url_prefix='/blog')

@blog_bp.route('/posts', methods=['POST'])
@jwt_required()
@permission_required(Permission.MANAGE_BLOG)
def create_blog_post():
    data = request.get_json()
    sanitized_data = sanitize_input(data)

    title = sanitized_data.get('title')
    content = sanitized_data.get('content')
    author_id = sanitized_data.get('author_id')
    category_id = sanitized_data.get('category_id')

    if not all([title, content, author_id]):
        return jsonify({"msg": "Missing required fields"}), 400

    new_post = BlogPost(
        title=title, 
        content=content, 
        author_id=author_id,
        category_id=category_id
    )
    db.session.add(new_post)
    db.session.commit()
    return jsonify({"msg": "Blog post created", "post_id": new_post.id}), 201

@blog_bp.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
@permission_required(Permission.MANAGE_BLOG)
def update_blog_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    data = request.get_json()
    sanitized_data = sanitize_input(data)

    post.title = sanitized_data.get('title', post.title)
    post.content = sanitized_data.get('content', post.content)
    post.category_id = sanitized_data.get('category_id', post.category_id)
    
    db.session.commit()
    return jsonify({"msg": "Blog post updated"}), 200

@blog_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
@permission_required(Permission.MANAGE_BLOG)
def delete_blog_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({"msg": "Blog post deleted"}), 200

# Routes for blog categories
@blog_bp.route('/categories', methods=['POST'])
@jwt_required()
@permission_required(Permission.MANAGE_BLOG)
def create_blog_category():
    data = request.get_json()
    sanitized_data = sanitize_input(data)
    name = sanitized_data.get('name')
    if not name:
        return jsonify({"msg": "Category name is required"}), 400

    if BlogCategory.query.filter_by(name=name).first():
        return jsonify({"msg": "Category already exists"}), 409
        
    new_category = BlogCategory(name=name)
    db.session.add(new_category)
    db.session.commit()
    return jsonify({"msg": "Category created", "category_id": new_category.id}), 201

@blog_bp.route('/categories', methods=['GET'])
@jwt_required()
@permission_required(Permission.MANAGE_BLOG)
def get_blog_categories():
    categories = BlogCategory.query.all()
    return jsonify([{'id': c.id, 'name': c.name} for c in categories])

@blog_bp.route('/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
@permission_required(Permission.MANAGE_BLOG)
def update_blog_category(category_id):
    category = BlogCategory.query.get_or_404(category_id)
    data = request.get_json()
    sanitized_data = sanitize_input(data)
    category.name = sanitized_data.get('name', category.name)
    db.session.commit()
    return jsonify({"msg": "Category updated"})

@blog_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
@permission_required(Permission.MANAGE_BLOG)
def delete_blog_category(category_id):
    category = BlogCategory.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({"msg": "Category deleted"})
