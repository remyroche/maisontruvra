from flask import Blueprint, request, jsonify
from backend.services.order_service import OrderService
from backend.utils.sanitization import sanitize_input
from backend.auth.permissions import admin_required, staff_required, roles_required, permissions_required
from ..utils.decorators import log_admin_action

order_management_bp = Blueprint('order_management_bp', __name__, url_prefix='/admin/orders')

# READ all orders (with pagination)
@order_management_bp.route('/', methods=['GET'])
@permissions_required('MANAGE_ORDERS')
@log_admin_action
@roles_required ('Admin', 'Manager', 'Support')
@admin_required
def get_orders():
    """
    Get a paginated list of all orders.
    Query Params:
    - page: integer, the page number to retrieve.
    - per_page: integer, the number of orders per page.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        # Assuming the service method is updated to handle pagination
        orders_pagination = OrderService.get_all_orders_paginated(page=page, per_page=per_page)
        return jsonify({
            "status": "success",
            "data": [order.to_dict() for order in orders_pagination.items],
            "total": orders_pagination.total,
            "pages": orders_pagination.pages,
            "current_page": orders_pagination.page
        }), 200
    except Exception as e:
        # In a real app, log the error e
        return jsonify(status="error", message="An internal error occurred while fetching orders."), 500

# READ a single order by ID
@order_management_bp.route('/<int:order_id>', methods=['GET'])
@permissions_required('MANAGE_ORDERS')
@log_admin_action
@roles_required ('Admin', 'Manager', 'Support')
@admin_required
def get_order(order_id):
    """
    Get a single order by its ID.
    """
    order = OrderService.get_order_by_id(order_id)
    if order:
        return jsonify(status="success", data=order.to_dict()), 200
    return jsonify(status="error", message="Order not found"), 404

# UPDATE an existing order's status
@order_management_bp.route('/<int:order_id>/status', methods=['PUT'])
@permissions_required('MANAGE_ORDERS')
@log_admin_action
@roles_required ('Admin', 'Manager', 'Support')
@admin_required
def update_order_status(order_id):
    """
    Update an existing order's status.
    """
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify(status="error", message="Invalid or missing 'status' in JSON body"), 400

    if not OrderService.get_order_by_id(order_id):
        return jsonify(status="error", message="Order not found"), 404

    sanitized_status = sanitize_input(data['status'])
    
    try:
        # Assuming the service handles the logic of status transition
        updated_order = OrderService.update_order_status(order_id, sanitized_status)
        return jsonify(status="success", data=updated_order.to_dict()), 200
    except ValueError as e: # Catch specific validation errors from the service
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # In a real app, log the error e
        return jsonify(status="error", message="An internal error occurred while updating the order status."), 500

# DELETE an order
@order_management_bp.route('/<int:order_id>', methods=['DELETE'])
@permissions_required('MANAGE_ORDERS')
@log_admin_action
@roles_required ('Admin', 'Manager', 'Support')
@admin_required
def delete_order(order_id):
    """
    Delete an order. This should be used with caution.
    """
    if not OrderService.get_order_by_id(order_id):
        return jsonify(status="error", message="Order not found"), 404

    try:
        OrderService.delete_order(order_id)
        return jsonify(status="success", message="Order deleted successfully"), 200
    except Exception as e:
        # In a real app, log the error e
        return jsonify(status="error", message="An internal error occurred while deleting the order."), 500

