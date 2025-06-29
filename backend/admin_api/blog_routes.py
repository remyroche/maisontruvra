from flask import Blueprint, jsonify, request
from backend.services.blog_service import BlogService
from backend.utils.decorators import jwt_required, staff_required, roles_required, permissions_required


blog_bp = Blueprint('admin_blog_routes', __name__, url_prefix='/api/admin/blog')

# Article Routes
@blog_bp.route('/articles', methods=['GET'])
@jwt_required()
@roles_required ('Admin', 'Editor', 'Manager')
def get_articles():
    articles = BlogService.get_all_articles()
    return jsonify([article.to_dict() for article in articles])

@blog_bp.route('/articles', methods=['POST'])
@jwt_required()
@roles_required ('Admin', 'Editor', 'Manager')
def create_article():
    data = request.get_json()
    article = BlogService.create_article(data)
    return jsonify(article.to_dict()), 201

@blog_bp.route('/articles/<int:article_id>', methods=['GET'])
@jwt_required()
@roles_required ('Admin', 'Editor', 'Manager')
def get_article(article_id):
    article = BlogService.get_article_by_id(article_id)
    if not article:
        return jsonify({"error": "Article not found"}), 404
    return jsonify(article.to_dict())

@blog_bp.route('/articles/<int:article_id>', methods=['PUT'])
@jwt_required()
@roles_required ('Admin', 'Editor', 'Manager')
def update_article(article_id):
    data = request.get_json()
    article = BlogService.update_article(article_id, data)
    if not article:
        return jsonify({"error": "Article not found"}), 404
    return jsonify(article.to_dict())

@blog_bp.route('/articles/<int:article_id>', methods=['DELETE'])
@jwt_required()
@roles_required ('Admin', 'Editor', 'Manager')
def delete_article(article_id):
    if BlogService.delete_article(article_id):
        return jsonify({"message": "Article deleted successfully"})
    return jsonify({"error": "Article not found"}), 404

# Blog Category Routes
@blog_bp.route('/categories', methods=['GET'])
@jwt_required()
@roles_required ('Admin', 'Editor', 'Manager')
def get_blog_categories():
    categories = BlogService.get_all_blog_categories()
    return jsonify([category.to_dict() for category in categories])

@blog_bp.route('/categories', methods=['POST'])
@jwt_required()
@roles_required ('Admin', 'Editor', 'Manager')
def create_blog_category():
    data = request.get_json()
    category = BlogService.create_blog_category(data['name'], data.get('description'))
    return jsonify(category.to_dict()), 201

@blog_bp.route('/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
@roles_required ('Admin', 'Editor', 'Manager')
def update_blog_category(category_id):
    data = request.get_json()
    category = BlogService.update_blog_category(category_id, data)
    if not category:
        return jsonify({"error": "Blog category not found"}), 404
    return jsonify(category.to_dict())

@blog_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
@roles_required ('Admin', 'Editor', 'Manager')
def delete_blog_category(category_id):
    if BlogService.delete_blog_category(category_id):
        return jsonify({"message": "Blog category deleted successfully"})
    return jsonify({"error": "Blog category not found"}), 404

