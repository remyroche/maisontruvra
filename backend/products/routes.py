from marshmallow import ValidationError
from backend.services.product_service import ProductService
from backend.utils.input_sanitizer import InputSanitizer
from backend.services.exceptions import NotFoundException, ValidationException
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import cache
import logging
from backend.services.review_service import ReviewService
from backend.schemas import ProductSearchSchema, ReviewSchema
from flask import Blueprint, request, jsonify, current_app
from backend.services.inventory_service import InventoryService
from backend.schemas import ProductSchema

products_bp = Blueprint('products', __name__, url_prefix='/api/products')
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)



@products_bp.route('/<uuid:product_id>/recommendations', methods=['GET'])
def get_recommendations(product_id):
    """Gets co-purchased product recommendations for a given product."""
    recommendations = ProductService.get_product_recommendations(product_id)
    return jsonify([product.to_dict() for product in recommendations])

@products_bp.route('/search', methods=['GET'])
def search_products():
    """Endpoint for product search/autocomplete."""
    query = InputSanitizer.InputSanitizer.sanitize_input(request.args.get('q', ''))
    if len(query) < 2:
        return jsonify([])
    
    products = ProductService.search_products(query)
    # Return a simpler dict for search results
    return jsonify([{
        'id': str(p.id), 
        'name': p.name, 
        'sku': p.sku
    } for p in products])


# READ all products with filtering, searching, and pagination
@cache.cached(timeout=21600)
@products_bp.route('/', methods=['GET'])
def get_products():
    """
    Get a list of all available products.
    Query Params:
    - page: The page number for pagination.
    - per_page: The number of items per page.
    - category: Filter by category slug or ID.
    - q: Search query for product name or description.
    """
    try:
        # Validate query parameters using marshmallow schema
        try:
            schema = ProductSearchSchema()
            validated_params = schema.load(request.args)
        except ValidationError as err:
            return jsonify(status="error", message="Invalid query parameters", errors=err.messages), 400

        page = validated_params.get('page', 1)
        per_page = validated_params.get('per_page', 24)
        category = validated_params.get('category')
        search_query = validated_params.get('q', '')

        filters = {'category': category, 'search': search_query}
        
        products_pagination = ProductService.get_all_products_paginated(page=page, per_page=per_page, filters=filters)
        
        return jsonify({
            "status": "success",
            "data": [product.to_dict_for_public() for product in products_pagination.items],
            "total": products_pagination.total,
            "pages": products_pagination.pages,
            "current_page": products_pagination.page
        }), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An error occurred while fetching products."), 500

# READ a single product by its slug
@products_bp.route('/<string:slug>', methods=['GET'])
@cache.cached(timeout=21600)
def get_product_by_slug(slug):
    """
    Get detailed information for a single product by its slug.
    """
    clean_slug = InputSanitizer.InputSanitizer.sanitize_input(slug)
    product = ProductService.get_product_by_slug(clean_slug)
    if not product:
        return jsonify(status="error", message="Product not found"), 404
        
    return jsonify(status="success", data=product.to_dict_for_public()), 200

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    logger = current_app.logger
    product_service = ProductService(logger)
    product = product_service.get_product_by_id(product_id)
    if product:
        return jsonify(product_schema.dump(product)), 200
    return jsonify({"error": "Product not found"}), 404

@products_bp.route('/<int:product_id>/notify-me', methods=['POST'])
def request_stock_notification(product_id):
    """
    Endpoint for users to request notification when a product is back in stock.
    """
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({"error": "Email is required."}), 400

    logger = current_app.logger
    inventory_service = InventoryService(logger)
    
    try:
        _, message = inventory_service.request_stock_notification(product_id, email)
        return jsonify({"message": message}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.exception(f"Failed to create stock notification request for product {product_id}")
        return jsonify({"error": "An internal error occurred."}), 500
        
# READ all product categories
@products_bp.route('/categories', methods=['GET'])
@cache.cached(timeout=21600)
def get_product_categories():
    """
    Get a list of all product categories.
    """
    try:
        categories = ProductService.get_all_categories()
        return jsonify(status="success", data=[c.to_dict() for c in categories]), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An error occurred while fetching categories."), 500

# READ reviews for a specific product
@products_bp.route('/<int:product_id>/reviews', methods=['GET'])
@cache.cached(timeout=21600)
def get_product_reviews(product_id):
    """
    Get all approved reviews for a specific product.
    """
    try:
        reviews = ReviewService.get_approved_reviews_for_product(product_id)
        return jsonify(status="success", data=[r.to_dict_for_public() for r in reviews]), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An error occurred while fetching reviews."), 500

# CREATE a new review for a product
@products_bp.route('/<int:product_id>/reviews', methods=['POST'])
@jwt_required()
def create_product_review(product_id):
    """
    Submit a new review for a product. Requires authentication.
    """
    user_id = get_jwt_identity()
    
    json_data = request.get_json()
    if not json_data:
        return jsonify(status="error", message="Invalid JSON data provided."), 400
    
    # Validate input using marshmallow schema
    try:
        schema = ReviewSchema()
        validated_data = schema.load(json_data)
    except ValidationError as err:
        return jsonify(status="error", message="Validation failed.", errors=err.messages), 400

    try:
        # The service layer should handle validation, e.g., if the user has purchased the product
        new_review = ReviewService.create_review(user_id, product_id, validated_data['rating'], validated_data.get('comment'))
        return jsonify(status="success", data=new_review.to_dict_for_public()), 201
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400 # Catches validation errors
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An error occurred while submitting your review."), 500

