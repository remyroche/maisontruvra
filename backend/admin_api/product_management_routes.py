from flask import Blueprint, request, jsonify
from backend.services.product_service import ProductService
from backend.utils.sanitization import sanitize_input
from backend.auth.permissions import admin_required, staff_required, roles_required, permissions_required
from ..utils.decorators import log_admin_action


product_management_bp = Blueprint('product_management_bp', __name__, url_prefix='/admin/products')

# CREATE a new product
@product_management_bp.route('/', methods=['POST'])
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
        return jsonify(status="success", data=new_product.to_dict()), 201
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred while creating the product."), 500

@admin_api_bp.route('/inventory/<int:inventory_id>', methods=['PUT'])
@log_admin_action
@roles_required ('Admin', 'Manager')
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
@product_management_bp.route('/', methods=['GET'])
@permissions_required('MANAGE_PRODUCTS')
@log_admin_action
@roles_required ('Admin', 'Manager', 'Support')
@admin_required
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
@log_admin_action
@roles_required ('Admin', 'Manager', 'Support')
@admin_required
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
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred while updating the product."), 500

# DELETE a product
@product_management_bp.route('/<int:product_id>', methods=['DELETE'])
@permissions_required('MANAGE_PRODUCTS')
@log_admin_action
@roles_required ('Admin', 'Manager')
@admin_required
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

