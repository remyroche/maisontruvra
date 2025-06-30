from flask import Blueprint, request, jsonify, g
from backend.utils.input_sanitizer import InputSanitizer
from backend.utils.decorators import staff_required, admin_required, roles_required, permissions_required, get_object_or_404, api_resource_handler
from backend.models.inventory_models import Inventory
from backend.extensions import cache, db
from backend.services.background_task_service import BackgroundTaskService
from backend.tasks import send_back_in_stock_email_task
from backend.schemas import CreateProductSchema
from marshmallow import ValidationError
from backend.schemas import CreateProductSchema, CreateProductInputSchema, ProductOutputSchema, InventoryUpdateSchema
from backend.models.product_models import Product
from backend.services.product_service import ProductService


product_management_bp = Blueprint('product_management_routes', __name__, url_prefix='/api/admin')
product_service = ProductService()
task_service = BackgroundTaskService()

# Initialize schema instances
product_output_schema = ProductOutputSchema()
products_output_schema = ProductOutputSchema(many=True)

# CREATE a new product
@product_management_bp.route('/products', methods=['POST'])
@api_resource_handler(Product, schema=CreateProductSchema(), check_ownership=False)
@permissions_required('MANAGE_PRODUCTS')
@roles_required ('Admin', 'Manager')
def create_product():
    """
    Create a new product.
    """
    product = ProductService.create_product(g.validated_data)

    try:
        cache.delete(ProductService.get_all_products)
        return jsonify(product_output_schema.dump(product)), 201
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred while creating the product."), 500


@product_management_bp.route('/', methods=['GET'])
@admin_required
def get_all_products():
    """
    Endpoint to get a list of all products.
    Uses the ProductOutputSchema (with many=True) for serialization.
    """
    products = ProductService.get_all_products()
    return jsonify(products_output_schema.dump(products)), 200
    
@product_management_bp.route('/products/import', methods=['POST'])
@roles_required ('Admin', 'Manager')
def import_products():
    """
    Starts a background task to import products from a CSV file.
    """
    # ... logic to handle file upload
    task = task_service.run_task('app.tasks.import_products_task', args=[...])
    return jsonify({"task_id": task.id}), 202

@product_management_bp.route('/inventory/<int:inventory_id>', methods=['PUT'])
@permissions_required('MANAGE_PRODUCTS')
@roles_required ('Admin', 'Manager', 'Farmer')
def update_inventory(inventory_id):
    """
    Updates the quantity of an inventory item and triggers back-in-stock
    notifications if the product was previously out of stock.
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Invalid JSON data provided"}), 400
    
    # Validate input using marshmallow schema
    try:
        schema = InventoryUpdateSchema()
        validated_data = schema.load(json_data)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "errors": err.messages}), 400

    inventory_item = Inventory.query.get(inventory_id)
    if not inventory_item:
        return jsonify({"error": "Inventory item not found"}), 404

    new_quantity = validated_data['quantity']
    cache.delete(f'view//api/products/{inventory_item.product_id}')
    cache.delete('view//api/products')

    # --- Back-in-Stock Notification Logic ---
    # Check the available stock *before* making changes
    was_out_of_stock = inventory_item.available_quantity <= 0
    
    # Update the total physical stock
    inventory_item.quantity = new_quantity
    db.session.commit()

    # Check the available stock *after* making changes
    is_now_in_stock = inventory_item.available_quantity > 0

    # If the status changed from out-of-stock to in-stock, trigger the task
    if was_out_of_stock and is_now_in_stock:
        # Use .delay() to run this as a background task via Celery
        send_back_in_stock_email_task.delay(inventory_item.product_id)
    # --- End Logic ---

    return jsonify({"message": f"Inventory for product {inventory_item.product_id} updated to {new_quantity}."}), 200

# READ all products (with pagination)
@product_management_bp.route('/products', methods=['GET'])
@permissions_required('MANAGE_PRODUCTS')
@roles_required ('Admin', 'Staff')
@cache.cached(timeout=21600)
def get_products():
    """
    Get a paginated list of all products.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Collect filter parameters from the request
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        search_query = request.args.get('search', None, type=str)
        
        filters = {'include_deleted': include_deleted}
        if search_query:
            filters['search'] = search_query
            
        products_pagination = ProductService.get_all_products_paginated(page=page, per_page=per_page, filters=filters)
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
@product_management_bp.route('/products/<int:product_id>', methods=['GET'])
@permissions_required('MANAGE_PRODUCTS')
@roles_required ('Admin', 'Manager', 'Support')
@cache.cached(timeout=21600)
@get_object_or_404(Product)
def get_product(product_id):
    product = ProductService.get_product_by_id(product_id)
    # The ProductNotFoundError is handled by the global error handler.
    return jsonify(product_output_schema.dump(product)), 200



# UPDATE an existing product
@product_management_bp.route('/products/<int:product_id>', methods=['PUT'])
@permissions_required('MANAGE_PRODUCTS')
@roles_required ('Admin', 'Manager')
@get_object_or_404(Product)
def update_product(product_id):
    """
    Update an existing product's information.
    """
    product_to_update = g.product
    data = request.get_json()
    
    updated_product = product_service.update_product(product_to_update.id, data)
    
    if updated_product:
        return jsonify(updated_product.to_dict_detailed())
    return jsonify({"error": "Failed to update product"}), 400
    
# DELETE a product
@product_management_bp.route('/products/<int:product_id>', methods=['DELETE'])
@permissions_required('MANAGE_PRODUCTS')
@roles_required ('Admin', 'Manager')
def delete_product(product_id):
    """
    Delete a product.
    """
    hard_delete = request.args.get('hard', 'false').lower() == 'true'
    if hard_delete:
        if ProductService.hard_delete_product(product_id):
            cache.delete('view//api/products')
            cache.delete(f'view//api/products/{product_id}')
            return jsonify(status="success", message="Product permanently deleted")
    else:
        if ProductService.soft_delete_product(product_id):
            cache.delete('view//api/products')
            cache.delete(f'view//api/products/{product_id}')
            return jsonify(status="success", message="Product soft-deleted successfully")
    return jsonify(status="error", message="Product not found"), 404

@product_management_bp.route('/products/<int:product_id>/restore', methods=['PUT'])
@permissions_required('MANAGE_PRODUCTS')
@roles_required ('Admin', 'Manager')
def restore_product(product_id):
    if ProductService.restore_product(product_id):
        return jsonify(status="success", message="Product restored successfully")
    return jsonify(status="error", message="Product not found"), 404



# --- Category Management ---

@product_management_bp.route('/categories', methods=['GET'])
@permissions_required('MANAGE_PRODUCTS')
@roles_required ('Admin', 'Staff')
@cache.cached(timeout=300, key_prefix='view_admin_categories')
def get_product_categories():
    """Gets all product categories."""
    categories = ProductService.get_all_categories()
    return jsonify([category.to_dict() for category in categories])

@product_management_bp.route('/categories', methods=['POST'])
@permissions_required('MANAGE_PRODUCTS')
@roles_required ('Admin', 'Manager')
def create_product_category():
    """Creates a new product category."""
    data = request.get_json()
    category = ProductService.create_category(data)
    cache.delete('view_admin_categories')
    return jsonify(category.to_dict()), 201

@product_management_bp.route('/categories/<int:category_id>', methods=['PUT'])
@permissions_required('MANAGE_PRODUCTS')
@roles_required ('Admin', 'Manager')
def update_product_category(category_id):
    """Updates a product category."""
    data = request.get_json()
    category = ProductService.update_category(category_id, data)
    if not category:
        return jsonify({"error": "Product category not found"}), 404
    cache.delete('view_admin_categories')
    return jsonify(category.to_dict())

@product_management_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@permissions_required('MANAGE_PRODUCTS')
@roles_required ('Admin', 'Manager')
def delete_product_category(category_id):
    """Deletes a product category."""
    hard_delete = request.args.get('hard', 'false').lower() == 'true'
    if hard_delete:
        if ProductService.hard_delete_category(category_id):
            cache.delete('view_admin_categories')
            return jsonify({"message": "Product category permanently deleted successfully"})
    else:
        if ProductService.delete_category(category_id):
            cache.delete('view_admin_categories')
            return jsonify({"message": "Product category deleted successfully"})
    return jsonify({"error": "Product category not found"}), 404

@product_management_bp.route('/categories/<int:category_id>/restore', methods=['PUT'])
@permissions_required('MANAGE_PRODUCTS')
@roles_required ('Admin', 'Manager')
def restore_product_category(category_id):
    """Restores a soft-deleted product category."""
    if ProductService.restore_category(category_id):
        cache.delete('view_admin_categories')
        return jsonify(status="success", message="Product category restored successfully")
    return jsonify(status="error", message="Product category not found"), 404



# --- Collection Management ---

@product_management_bp.route('/collections', methods=['GET'])
@permissions_required('MANAGE_PRODUCTS')
@roles_required ('Admin', 'Staff')
@cache.cached(timeout=300, key_prefix='view_admin_collections')
def get_product_collections():
    """Gets all product collections."""
    collections = ProductService.get_all_collections()
    return jsonify([collection.to_dict() for collection in collections])

@product_management_bp.route('/collections', methods=['POST'])
@permissions_required('MANAGE_PRODUCTS')
@roles_required ('Admin', 'Manager')
def create_product_collection():
    """Creates a new product collection."""
    data = request.get_json()
    collection = ProductService.create_collection(data)
    cache.delete('view_admin_collections')
    return jsonify(collection.to_dict()), 201

@product_management_bp.route('/collections/<int:collection_id>', methods=['PUT'])
@permissions_required('MANAGE_PRODUCTS')
@roles_required ('Admin', 'Manager')
def update_product_collection(collection_id):
    """Updates a product collection."""
    data = request.get_json()
    collection = ProductService.update_collection(collection_id, data)
    if not collection:
        return jsonify({"error": "Product collection not found"}), 404
    cache.delete('view_admin_collections')
    return jsonify(collection.to_dict())

@product_management_bp.route('/collections/<int:collection_id>', methods=['DELETE'])
@permissions_required('MANAGE_PRODUCTS')
@roles_required ('Admin', 'Manager')
def delete_product_collection(collection_id):
    """Deletes a product collection."""
    hard_delete = request.args.get('hard', 'false').lower() == 'true'
    if hard_delete:
        if ProductService.hard_delete_collection(collection_id):
            cache.delete('view_admin_collections')
            return jsonify({"message": "Product collection permanently deleted successfully"})
    else:
        if ProductService.delete_collection(collection_id):
            cache.delete('view_admin_collections')
            return jsonify({"message": "Product collection deleted successfully"})
    return jsonify({"error": "Product collection not found"}), 404

@product_management_bp.route('/collections/<int:collection_id>/restore', methods=['PUT'])
@permissions_required('MANAGE_PRODUCTS')
@roles_required ('Admin', 'Manager')
def restore_product_collection(collection_id):
    """Restores a soft-deleted product collection."""
    if ProductService.restore_collection(collection_id):
        cache.delete('view_admin_collections')
        return jsonify(status="success", message="Product collection restored successfully")
    return jsonify(status="error", message="Product collection not found"), 404
