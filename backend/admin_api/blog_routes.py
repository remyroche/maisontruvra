from flask import Blueprint, request, jsonify
from backend.services.product_service import ProductService # Assuming blog is managed under product-like service
from backend.auth.permissions import admin_required

blog_routes = Blueprint('admin_blog_routes', __name__)

@blog_routes.route('/blog/posts', methods=['POST'])
@admin_required
def create_blog_post():
    data = request.get_json()
    # Simplified: using ProductService to create a 'blog' type product
    # In a real app, this would be a dedicated BlogService
    data['product_type'] = 'blog'
    post = ProductService.create_product(data)
    return jsonify(post.to_dict()), 201

@blog_routes.route('/blog/posts', methods=['GET'])
@admin_required
def get_blog_posts():
    # Simplified: using ProductService to get 'blog' type products
    posts = ProductService.get_products_by_type('blog')
    return jsonify([p.to_dict() for p in posts]), 200

@blog_routes.route('/blog/posts/<int:post_id>', methods=['PUT'])
@admin_required
def update_blog_post(post_id):
    data = request.get_json()
    post = ProductService.update_product(post_id, data)
    return jsonify(post.to_dict()), 200

@blog_routes.route('/blog/posts/<int:post_id>', methods=['DELETE'])
@admin_required
def delete_blog_post(post_id):
    ProductService.delete_product(post_id)
    return jsonify({'message': 'Blog post deleted'}), 200
