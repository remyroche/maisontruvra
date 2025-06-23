from flask import Blueprint, request, jsonify
from backend.services.product_service import ProductService
from backend.utils.sanitization import sanitize_input
from backend.auth.permissions import permissions_required

product_management_bp = Blueprint('product_management_bp', __name__, url_prefix='/admin/products')

# CREATE a new product
@product_management_bp.route('/', methods=['POST'])
@permissions_required('MANAGE_PRODUCTS')
def create_product():
    """
    Create a new product.
    """
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Invalid or missing JSON body"), 400

    sanitized_data = sanitize_input(data)

    required_fields = ['name', 'description', 'price', 'category_id']
    if not all(field in sanitized_data for field in required_fields):
        missing_fields = [field for field in required_fields if field not in sanitized_data]
        return jsonify(status="error", message=f"Missing required fields: {', '.join(missing_fields)}"), 400

    try:
        new_product = ProductService.create_product(sanitized_data)
        return jsonify(status="success", data=new_product.to_dict()), 201
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred while creating the product."), 500

# READ all products (with pagination)
@product_management_bp.route('/', methods=['GET'])
@permissions_required('MANAGE_PRODUCTS')
def get_products():
    """
    Get a paginated list of all products.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        products_pagination = ProductService.get_all_products_paginated(page=page, per_page=per_page)
        return jsonify({
            "status": "success",
            "data": [product.to_dict() for product in products_pagination.items],
            "total": products_pagination.total,
            "pages": products_pagination.pages,
            "current_page": products_pagination.page
        }), 200
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred while fetching products."), 500

# READ a single product by ID
@product_management_bp.route('/<int:product_id>', methods=['GET'])
@permissions_required('MANAGE_PRODUCTS')
def get_product(product_id):
    """
    Get a single product by their ID.
    """
    product = ProductService.get_product_by_id(product_id)
    if product:
        return jsonify(status="success", data=product.to_dict()), 200
    return jsonify(status="error", message="Product not found"), 404

# UPDATE an existing product
@product_management_bp.route('/<int:product_id>', methods=['PUT'])
@permissions_required('MANAGE_PRODUCTS')
def update_product(product_id):
    """
    Update an existing product's information.
    """
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Invalid or missing JSON body"), 400
    
    if not ProductService.get_product_by_id(product_id):
        return jsonify(status="error", message="Product not found"), 404

    sanitized_data = sanitize_input(data)

    try:
        updated_product = ProductService.update_product(product_id, sanitized_data)
        return jsonify(status="success", data=updated_product.to_dict()), 200
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred while updating the product."), 500

# DELETE a product
@product_management_bp.route('/<int:product_id>', methods=['DELETE'])
@permissions_required('MANAGE_PRODUCTS')
def delete_product(product_id):
    """
    Delete a product.
    """
    if not ProductService.get_product_by_id(product_id):
        return jsonify(status="error", message="Product not found"), 404

    try:
        ProductService.delete_product(product_id)
        return jsonify(status="success", message="Product deleted successfully"), 200
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred while deleting the product."), 500

