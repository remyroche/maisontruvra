from flask import Blueprint, request, jsonify
from backend.services.product_service import ProductService
from backend.utils.sanitization import sanitize_input
from backend.auth.permissions import admin_required, staff_required, roles_required, permissions_required
from backend.models.inventory_models import Inventory
from backend.extensions import cache
from ..utils.decorators import log_admin_action

product_management_bp = Blueprint('product_management_routes', __name__, url_prefix='/api/admin')

# CREATE a new product
@product_management_bp.route('/products', methods=['POST'])
@permissions_required('MANAGE_PRODUCTS')
@log_admin_action
@roles_required ('Admin', 'Manager')
@admin_required
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
        cache.delete('view//api/products')
        return jsonify(status="success", data=new_product.to_dict()), 201
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred while creating the product."), 500

@product_management_bp.route('/inventory/<int:inventory_id>', methods=['PUT'])
@permissions_required('MANAGE_PRODUCTS')
@log_admin_action
@roles_required ('Admin', 'Manager', 'Farmer')
@admin_required
def update_inventory(inventory_id):
    """
    Updates the quantity of an inventory item and triggers back-in-stock
    notifications if the product was previously out of stock.
    """
    data = request.get_json()
    if 'quantity' not in data:
        return jsonify({"error": "Quantity is required"}), 400

    inventory_item = Inventory.query.get(inventory_id)
    if not inventory_item:
        return jsonify({"error": "Inventory item not found"}), 404

    try:
        new_quantity = int(data['quantity'])
        cache.delete('view//api/products')
        cache.delete('view//api/products/{}'.format(product_id))
    except ValueError:
        return jsonify({"error": "Invalid quantity format"}), 400

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
        send_back_in_stock_emails_task.delay(inventory_item.product_id)
    # --- End Logic ---

    return jsonify({"message": f"Inventory for product {inventory_item.product_id} updated to {new_quantity}."}), 200

# READ all products (with pagination)
@product_management_bp.route('/products', methods=['GET'])
@permissions_required('MANAGE_PRODUCTS')
@log_admin_action
@roles_required ('Admin', 'Staff')
@admin_required
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
@log_admin_action
@roles_required ('Admin', 'Manager', 'Support')
@admin_required
@cache.cached(timeout=21600)
def get_product(product_id):
    """
    Get a single product by their ID.
    """
    product = ProductService.get_product_by_id(product_id)
    if product:
        return jsonify(status="success", data=product.to_dict()), 200
    return jsonify(status="error", message="Product not found"), 404

# UPDATE an existing product
@product_management_bp.route('/products/<int:product_id>', methods=['PUT'])
@permissions_required('MANAGE_PRODUCTS')
@log_admin_action
@roles_required ('Admin', 'Manager')
@admin_required
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
        cache.delete('view//api/products') 
        cache.delete('view//api/products/{}'.format(product_id))
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred while updating the product."), 500

# DELETE a product
@product_management_bp.route('/products/<int:product_id>', methods=['DELETE'])
@permissions_required('MANAGE_PRODUCTS')
@log_admin_action
@roles_required ('Admin', 'Manager')
@admin_required
def delete_product(product_id):
    """
    Delete a product.
    """
    hard_delete = request.args.get('hard', 'false').lower() == 'true'
    cache.delete('view//api/products') 
    cache.delete('view//api/products/{}'.format(product_id))
    if hard_delete:
        if ProductService.hard_delete_product(product_id):
            return jsonify(status="success", message="Product permanently deleted")
    else:
        if ProductService.soft_delete_product(product_id):
            return jsonify(status="success", message="Product soft-deleted successfully")
    return jsonify(status="error", message="Product not found"), 404

@product_management_bp.route('/products/<int:product_id>/restore', methods=['PUT'])
@permissions_required('MANAGE_PRODUCTS')
@log_admin_action
@roles_required ('Admin', 'Manager')
@admin_required
def restore_product(product_id):
    if ProductService.restore_product(product_id):
        return jsonify(status="success", message="Product restored successfully")
    return jsonify(status="error", message="Product not found"), 404



# Product Category Routes
@cache.cached(timeout=21600)
@product_management_bp.route('/product-categories', methods=['GET'])
@permissions_required('MANAGE_PRODUCTS')
@log_admin_action
@roles_required ('Admin', 'Staff')
@admin_required
def get_product_categories():
    categories = ProductService.get_all_categories()
    return jsonify([category.to_dict() for category in categories])

@product_management_bp.route('/product-categories', methods=['POST'])
@permissions_required('MANAGE_PRODUCTS')
@log_admin_action
@roles_required ('Admin', 'Manager')
@admin_required
def create_product_category():
    data = request.get_json()
    category = ProductService.create_category(data)
    return jsonify(category.to_dict()), 201

@product_management_bp.route('/product-categories/<int:category_id>', methods=['PUT'])
@permissions_required('MANAGE_PRODUCTS')
@log_admin_action
@roles_required ('Admin', 'Manager')
@admin_required
def update_product_category(category_id):
    data = request.get_json()
    category = ProductService.update_category(category_id, data)
    if not category:
        return jsonify({"error": "Product category not found"}), 404
    return jsonify(category.to_dict())

@product_management_bp.route('/product-categories/<int:category_id>', methods=['DELETE'])
@permissions_required('MANAGE_PRODUCTS')
@log_admin_action
@roles_required ('Admin', 'Manager')
@admin_required
def delete_product_category(category_id):
    hard_delete = request.args.get('hard', 'false').lower() == 'true'
    if hard_delete:
        if ProductService.hard_delete_category(category_id):
            return jsonify({"message": "Product category permanently deleted successfully"})
    else:
        if ProductService.delete_category(category_id):
            return jsonify({"message": "Product category deleted successfully"})
    return jsonify({"error": "Product category not found"}), 404

@product_management_bp.route('/product-categories/<int:category_id>/restore', methods=['PUT'])
@permissions_required('MANAGE_PRODUCTS')
@log_admin_action
@roles_required ('Admin', 'Manager')
@admin_required
def restore_product_category(category_id):
    if ProductService.restore_category(category_id):
        return jsonify(status="success", message="Product category restored successfully")
    return jsonify(status="error", message="Product category not found"), 404



# Product Collection Routes
@cache.cached(timeout=21600)
@product_management_bp.route('/product-collections', methods=['GET'])
@permissions_required('MANAGE_PRODUCTS')
@log_admin_action
@roles_required ('Admin', 'Staff')
@admin_required
def get_product_collections():
    collections = ProductService.get_all_collections()
    return jsonify([collection.to_dict() for collection in collections])

@product_management_bp.route('/product-collections', methods=['POST'])
@permissions_required('MANAGE_PRODUCTS')
@log_admin_action
@roles_required ('Admin', 'Manager')
@admin_required
def create_product_collection():
    data = request.get_json()
    collection = ProductService.create_collection(data)
    return jsonify(collection.to_dict()), 201

@product_management_bp.route('/product-collections/<int:collection_id>', methods=['PUT'])
@permissions_required('MANAGE_PRODUCTS')
@log_admin_action
@roles_required ('Admin', 'Manager')
@admin_required
def update_product_collection(collection_id):
    data = request.get_json()
    collection = ProductService.update_collection(collection_id, data)
    if not collection:
        return jsonify({"error": "Product collection not found"}), 404
    return jsonify(collection.to_dict())

@product_management_bp.route('/product-collections/<int:collection_id>', methods=['DELETE'])
@permissions_required('MANAGE_PRODUCTS')
@log_admin_action
@roles_required ('Admin', 'Manager')
@admin_required
def delete_product_collection(collection_id):
    hard_delete = request.args.get('hard', 'false').lower() == 'true'
    if hard_delete:
        if ProductService.hard_delete_collection(collection_id):
            return jsonify({"message": "Product collection permanently deleted successfully"})
    else:
        if ProductService.delete_collection(collection_id):
            return jsonify({"message": "Product collection deleted successfully"})
    return jsonify({"error": "Product collection not found"}), 404

@product_management_bp.route('/product-collections/<int:collection_id>/restore', methods=['PUT'])
@permissions_required('MANAGE_PRODUCTS')
@log_admin_action
@roles_required ('Admin', 'Manager')
@admin_required
def restore_product_collection(collection_id):
    if ProductService.restore_collection(collection_id):
        return jsonify(status="success", message="Product collection restored successfully")
    return jsonify(status="error", message="Product collection not found"), 404
