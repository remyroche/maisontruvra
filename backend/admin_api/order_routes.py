from flask import Blueprint, request, jsonify, g
from backend.services.order_service import OrderService
from backend.utils.input_sanitizer import InputSanitizer
from backend.utils.decorators import staff_required, roles_required, permissions_required, api_resource_handler
from backend.models.order_models import Order
from backend.schemas import OrderStatusUpdateSchema

order_routes = Blueprint('admin_order_routes', __name__, url_prefix='/api/admin/orders')

@order_routes.route('/<int:order_id>', methods=['GET'])
@api_resource_handler(Order, check_ownership=False)
@permissions_required('MANAGE_ORDERS')
@roles_required ('Admin', 'Manager', 'Support')
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
    # Order is already validated and available as g.order
    return jsonify(g.order.to_dict(include_details=True))


@order_routes.route('/<int:order_id>/status', methods=['PUT'])
@api_resource_handler(Order, schema=OrderStatusUpdateSchema(), check_ownership=False)
@permissions_required('MANAGE_ORDERS')
@roles_required ('Admin', 'Manager', 'Support')
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
    try:
        updated_order = OrderService.update_order_status(order_id, g.validated_data['status'])
        if not updated_order:
            return jsonify({"error": "Order not found"}), 404
        return jsonify(updated_order.to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
        
@order_routes.route('/', methods=['GET'])
@permissions_required('MANAGE_ORDERS')
@roles_required ('Admin', 'Manager', 'Support')
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




# DELETE an order
@order_routes.route('/<int:order_id>', methods=['DELETE'])
@api_resource_handler(Order, check_ownership=False)
@permissions_required('MANAGE_ORDERS')
@roles_required ('Admin', 'Manager', 'Support')
def delete_order(order_id):
    """
    Delete an order. This should be used with caution.
    """
    try:
        OrderService.delete_order(order_id)
        return jsonify(status="success", message="Order deleted successfully"), 200
    except Exception as e:
        # In a real app, log the error e
        return jsonify(status="error", message="An internal error occurred while deleting the order."), 500

