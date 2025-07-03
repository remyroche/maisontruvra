"""
This module defines the API endpoints for product management in the admin panel.
It leverages the @api_resource_handler to create clean, secure, and consistent CRUD endpoints.
"""
from flask import Blueprint, request, g, jsonify, jwt_required
from ..models import Product
from ..schemas import ProductSchema
from ..utils.decorators import api_resource_handler, roles_required
from ..services.product_service import ProductService
from ..services.background_task_service import BackgroundTaskService
from backend.services.exceptions import ServiceException

# --- Blueprint Setup ---
bp = Blueprint('product_management', __name__, url_prefix='/api/admin/products')

# --- Product Endpoints ---

@bp.route('/', methods=['GET'])
@jwt_required()
@roles_required('Admin', 'Manager')
def get_all_products():
    """
    Retrieves a paginated list of all products.
    Supports including soft-deleted items via a query parameter.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        
        paginated_products = ProductService.get_all_products_paginated(
            page=page, 
            per_page=per_page, 
            include_deleted=include_deleted
        )
        
        return jsonify({
            "data": ProductSchema(many=True).dump(paginated_products.items),
            "total": paginated_products.total,
            "pages": paginated_products.pages,
            "current_page": paginated_products.page
        })
    except ServiceException as e:
        return jsonify(e.to_dict()), e.status_code


@bp.route('/', methods=['POST'])
@jwt_required()
@roles_required('Admin', 'Manager')
@api_resource_handler(model=Product, request_schema=ProductSchema, response_schema=ProductSchema, log_action=True)
def create_product():
    """
    Creates a new product.
    The decorator handles validation, session management, and response serialization.
    """
    return ProductService.create_product(g.validated_data)


@bp.route('/<int:product_id>', methods=['GET'])
@jwt_required()
@roles_required('Admin', 'Manager')
@api_resource_handler(model=Product, response_schema=ProductSchema, eager_loads=['category', 'variants', 'tags'])
def get_product(product_id):
    """
    Retrieves a single product by its ID.
    The decorator handles fetching and serialization.
    """
    return g.target_object


@bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
@roles_required('Admin', 'Manager')
@api_resource_handler(model=Product, request_schema=ProductSchema, response_schema=ProductSchema, log_action=True)
def update_product(product_id):
    """
    Updates an existing product.
    The decorator fetches the product, validates input, and handles the response.
    """
    return ProductService.update_product(g.target_object, g.validated_data)


@bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
@roles_required('Admin', 'Manager')
@api_resource_handler(model=Product, allow_hard_delete=True, log_action=True)
def delete_product(product_id):
    """
    Deletes a product.
    - Soft-delete by default.
    - Use ?hard=true for a permanent, irreversible delete.
    The decorator handles all fetching and deletion logic automatically.
    """
    return None


@bp.route('/<int:product_id>/restore', methods=['POST'])
@jwt_required()
@roles_required('Admin', 'Manager')
@api_resource_handler(model=Product, response_schema=ProductSchema, log_action=True)
def restore_product(product_id):
    """
    Restores a soft-deleted product.
    The decorator handles all fetching and restoration logic automatically.
    """
    return g.target_object


@bp.route('/import', methods=['POST'])
@jwt_required()
@roles_required('Admin', 'Manager')
def import_products():
    """
    Starts a background task to import products from an uploaded CSV file.
    A more complete implementation would handle the file upload itself.
    """
    try:
        # In a real application, you would get the file from the request
        # and save it to a temporary path.
        # e.g., file = request.files['file']
        # temp_path = f"/tmp/{secure_filename(file.filename)}"
        # file.save(temp_path)
        
        # For demonstration, we use a placeholder path.
        file_path_placeholder = "path/to/uploaded/file.csv"
        
        task = BackgroundTaskService.run_task('app.tasks.import_products_task', args=[file_path_placeholder])
        return jsonify({"message": "Product import started.", "task_id": task.id}), 202
    except Exception as e:
        # A generic error handler for the import endpoint
        return jsonify({"message": f"Failed to start import task: {str(e)}"}), 500
