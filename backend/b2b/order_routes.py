from flask import Blueprint, request, jsonify
from backend.auth.permissions import b2b_user_required
from flask_jwt_extended import get_jwt_identity
from backend.services.order_service import OrderService
from backend.services.exceptions import ServiceException

order_routes = Blueprint('b2b_order_routes', __name__)

@order_routes.route('/quick-order', methods=['POST'])
@b2b_user_required
def quick_order():
    """
    Allows B2B users to place a quick order, often using SKUs.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    items = data.get('items') # Expects a list of {'sku': '...', 'quantity': ...}

    if not items:
        return jsonify({"error": "Order items are required."}), 400

    try:
        order = OrderService.create_b2b_quick_order(user_id, items)
        return jsonify(order.to_dict()), 201
    except ServiceException as e:
        return jsonify({"error": str(e)}), 400

@order_routes.route('/reorder/<int:order_id>', methods=['POST'])
@b2b_user_required
def reorder(order_id):
    """
    Creates a new cart or order based on a previous order.
    """
    user_id = get_jwt_identity()
    try:
        new_order = OrderService.reorder(user_id, order_id)
        return jsonify(new_order.to_dict()), 201
    except ServiceException as e:
        return jsonify({"error": str(e)}), 400
