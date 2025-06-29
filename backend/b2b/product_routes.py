from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from backend.services.product_service import ProductService
from backend.utils.input_sanitizer import InputSanitizer
from backend.utils.decorators import b2b_user_required

b2b_product_bp = Blueprint('b2b_product_bp', __name__, url_prefix='/api/b2b/products')

# READ all products with B2B pricing
def get_b2b_product(product_id):
    user_id = get_jwt_identity()
    try:
        product = ProductService.get_b2b_product_by_id(product_id, user_id)
        if product:
            return jsonify(status="success", data=product), 200
        return jsonify(status="error", message="Product not found"), 404
    except Exception as e:
        return jsonify(status="error", message="An internal error occurred."), 500

def get_b2b_products():
    user_id = get_jwt_identity()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        products_data, total, pages, current_page = ProductService.get_b2b_products_paginated(
            user_id=user_id,
            page=page,
            per_page=per_page,
            category=request.args.get('category'),
            collection=request.args.get('collection'),
            search_term=request.args.get('q')
        )
        return jsonify({
            "status": "success",
            "data": products_data,
            "total": total,
            "pages": pages,
            "current_page": current_page
        }), 200
    except Exception as e:
        return jsonify(status="error", message="An internal error occurred while fetching products."), 500
