from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from backend.services.product_service import ProductService
from backend.utils.sanitization import sanitize_input
from backend.auth.permissions import b2b_user_required

b2b_product_bp = Blueprint('b2b_product_bp', __name__, url_prefix='/api/b2b/products')

# READ all products with B2B pricing
@b2b_product_bp.route('/', methods=['GET'])
@b2b_user_required
def get_b2b_products():
    """
    Get a paginated and searchable list of all products, with B2B-specific pricing.
    """
    user_id = get_jwt_identity()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search_query = sanitize_input(request.args.get('q', ''))
        
        # This service method should handle fetching products and applying B2B pricing rules.
        products_pagination = ProductService.get_b2b_products_paginated(
            user_id,
            page=page,
            per_page=per_page,
            search_query=search_query
        )
        
        return jsonify({
            "status": "success",
            # The serializer should be aware of B2B pricing
            "data": [product.to_dict_for_b2b() for product in products_pagination.items],
            "total": products_pagination.total,
            "pages": products_pagination.pages,
            "current_page": products_pagination.page
        }), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal error occurred while fetching products."), 500

# READ a single product by ID with B2B pricing
@b2b_product_bp.route('/<int:product_id>', methods=['GET'])
@b2b_user_required
def get_b2b_product(product_id):
    """
    Get a single product by its ID, with B2B-specific pricing.
    """
    user_id = get_jwt_identity()
    try:
        product = ProductService.get_b2b_product_by_id(product_id, user_id)
        if product:
            return jsonify(status="success", data=product.to_dict_for_b2b()), 200
        return jsonify(status="error", message="Product not found"), 404
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal error occurred."), 500

