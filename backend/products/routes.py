from flask import Blueprint, jsonify, request
from backend.services.product_service import ProductService
from backend.services.recommendation_service import RecommendationService

products_bp = Blueprint('public_product_routes', __name__)

@products_bp.route('/', methods=['GET'])
def get_all_products():
    """
    Get a list of all published products, with optional filtering.
    """
    category_slug = request.args.get('category')
    collection_slug = request.args.get('collection')
    
    products = ProductService.get_all_published_products(
        category_slug=category_slug,
        collection_slug=collection_slug
    )
    return jsonify([p.to_dict() for p in products]), 200

@products_bp.route('/<string:slug>', methods=['GET'])
def get_product_details(slug):
    """
    Get the details for a single product by its slug.
    """
    product = ProductService.get_product_by_slug(slug)
    if not product or not product.is_published:
        return jsonify({"error": "Product not found"}), 404
        
    return jsonify(product.to_dict()), 200

@products_bp.route('/<int:product_id>/recommendations', methods=['GET'])
def get_recommendations(product_id):
    """
    Get product recommendations related to the given product.
    """
    recommendations = RecommendationService.get_recommendations_for_product(product_id)
    return jsonify([p.to_dict() for p in recommendations]), 200
