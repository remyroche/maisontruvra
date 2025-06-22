from flask import Blueprint, jsonify, abort
from backend.services.product_service import ProductService

blog_bp = Blueprint('blog_bp', __name__)

@blog_bp.route('/posts', methods=['GET'])
def get_published_posts():
    """
    Get all published blog posts.
    """
    # Simplified: using ProductService to get 'blog' type products.
    # A real implementation would likely have a dedicated BlogService with more features.
    posts = ProductService.get_published_products_by_type('blog')
    return jsonify([p.to_dict() for p in posts]), 200

@blog_bp.route('/posts/<string:slug>', methods=['GET'])
def get_post_by_slug(slug):
    """
    Get a single blog post by its slug.
    """
    post = ProductService.get_product_by_slug(slug)
    if not post or post.product_type != 'blog':
        abort(404, description="Blog post not found.")
    
    return jsonify(post.to_dict()), 200

@blog_bp.route('/categories', methods=['GET'])
def get_blog_categories():
    """
    Get all blog post categories.
    """
    # This might need a dedicated service method to distinguish blog categories
    # from product categories if they share the same model.
    categories = ProductService.get_all_categories() # Assuming shared categories for now
    return jsonify([c.to_dict() for c in categories]), 200