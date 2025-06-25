from flask import Blueprint, request, jsonify
from backend.services.order_service import OrderService
from backend.utils.sanitization import sanitize_input
from backend.auth.permissions import admin_required, staff_required, roles_required, permissions_required
from ..utils.decorators import log_admin_action

order_routes = Blueprint('admin_order_routes', __name__, url_prefix='/api/admin/orders')

@order_routes.route('/<int:order_id>', methods=['GET'])
@permissions_required('MANAGE_ORDERS')
@log_admin_action
@roles_required ('Admin', 'Manager', 'Support')
@admin_required
def get_order_details(order_id):
    """
    Retrieves details for a specific order.
    ---
    tags:
      - Admin Orders
    parameters:
      - in: path
        name: order_id
        required: true
        schema:
          type: integer
    security:
      - cookieAuth: []
    responses:
      200:
        description: Detailed information about the order.
      404:
        description: Order not found.
    """
    order = OrderService.get_order_by_id(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order.to_dict(include_details=True))


@order_routes.route('/<int:order_id>/status', methods=['PUT'])
@permissions_required('MANAGE_ORDERS')
@log_admin_action
@roles_required ('Admin', 'Manager', 'Support')
@admin_required
def update_order_status(order_id):
    """
    Updates the status of a specific order.
    ---
    tags:
      - Admin Orders
    parameters:
      - in: path
        name: order_id
        required: true
        schema:
          type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            status:
              type: string
              description: The new status for the order.
    security:
      - cookieAuth: []
    responses:
      200:
        description: Order status updated successfully.
      400:
        description: Invalid status provided.
      404:
        description: Order not found.
    """
    data = request.get_json()
    new_status = data.get('status')
    if not new_status:
        return jsonify({"error": "Status is required"}), 400
    
    try:
        updated_order = OrderService.update_order_status(order_id, new_status)
        if not updated_order:
            return jsonify({"error": "Order not found"}), 404
        return jsonify(updated_order.to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
        
@order_routes.route('/', methods=['GET'])
@permissions_required('MANAGE_ORDERS')
@log_admin_action
@roles_required ('Admin', 'Manager', 'Support')
@admin_required
def get_orders():
    """
    Retrieves all orders with optional filtering.
    ---
    tags:
      - Admin Orders
    parameters:
      - in: query
        name: status
        schema:
          type: string
        description: Filter orders by status.
      - in: query
        name: user_id
        schema:
          type: string
        description: Filter orders by user ID.
    security:
      - cookieAuth: []
    responses:
      200:
        description: A list of orders.
    """
    status = request.args.get('status')
    user_id = request.args.get('user_id')
    orders = OrderService.get_all_orders(status=status, user_id=user_id)
    return jsonify([order.to_dict() for order in orders])


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

