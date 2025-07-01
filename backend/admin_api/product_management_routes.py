"""
This module defines the API endpoints for product management in the admin panel.
It leverages the @api_resource_handler to create clean, secure, and consistent CRUD endpoints.
"""
from flask import Blueprint, request, g, jsonify
from ..models import Product
from ..schemas import ProductSchema
from ..utils.decorators import api_resource_handler, roles_required
from ..services.product_service import ProductService
from ..services.background_task_service import BackgroundTaskService

# --- Blueprint Setup ---
bp = Blueprint('product_management', __name__, url_prefix='/api/admin/products')

# --- Product Endpoints ---

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/<int:product_id>', methods=['GET', 'PUT', 'DELETE'])
@roles_required('Admin', 'Manager')
@api_resource_handler(
    model=Product,
    request_schema=ProductSchema,
    response_schema=ProductSchema,
    eager_loads=['category', 'variants', 'tags'],
    log_action=True,
    cache_timeout=600
)
def handle_products(product_id=None):
    """Handles all CRUD operations for Products."""
    if request.method == 'GET' and product_id is None:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        paginated_products = ProductService.get_all_products_paginated(page=page, per_page=per_page)
        return jsonify({
            "data": ProductSchema(many=True).dump(paginated_products.items),
            "total": paginated_products.total,
            "pages": paginated_products.pages,
            "current_page": paginated_products.page
        })

    if request.method == 'GET':
        return g.target_object
    elif request.method == 'POST':
        return ProductService.create_product(g.validated_data)
    elif request.method == 'PUT':
        return ProductService.update_product(product_id, g.validated_data)
    elif request.method == 'DELETE':
        hard_delete = request.args.get('hard', 'false').lower() == 'true'
        if hard_delete:
            ProductService.hard_delete_product(product_id)
        else:
            ProductService.soft_delete_product(product_id)
        return None

@bp.route('/<int:product_id>/restore', methods=['PUT'])
@roles_required('Admin', 'Manager')
def restore_product(product_id):
    """Restores a soft-deleted product."""
    ProductService.restore_product(product_id)
    return jsonify(message="Product restored successfully.")

@bp.route('/import', methods=['POST'])
@roles_required('Admin', 'Manager')
def import_products():
    """Starts a background task to import products from a CSV file."""
    task = BackgroundTaskService.run_task('app.tasks.import_products_task', args=["path/to/uploaded/file.csv"])
    return jsonify({"task_id": task.id}), 202
