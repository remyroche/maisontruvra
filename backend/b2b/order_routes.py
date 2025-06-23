from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.b2b_service import B2BService
from backend.utils.sanitization import sanitize_input
from backend.auth.permissions import b2b_user_required

b2b_order_routes_bp = Blueprint('b2b_order_routes_bp', __name__, url_prefix='/api/b2b/orders')

# GET the B2B user's order history
@b2b_order_routes_bp.route('/', methods=['GET'])
@b2b_user_required
def get_b2b_order_history():
    """
    Get a paginated list of the B2B user's order history.
    """
    user_id = get_jwt_identity()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        orders_pagination = B2BService.get_user_orders_paginated(user_id, page=page, per_page=per_page)
        
        return jsonify({
            "status": "success",
            "data": [order.to_dict_for_user() for order in orders_pagination.items],
            "total": orders_pagination.total,
            "pages": orders_pagination.pages,
            "current_page": orders_pagination.page
        }), 200
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred while fetching your orders."), 500

# GET a single B2B order by ID
@b2b_order_routes_bp.route('/<int:order_id>', methods=['GET'])
@b2b_user_required
def get_b2b_order(order_id):
    """
    Get a single B2B order by its ID, ensuring it belongs to the user.
    """
    user_id = get_jwt_identity()
    try:
        order = B2BService.get_order_by_id_for_user(order_id, user_id)
        if order:
            return jsonify(status="success", data=order.to_dict_for_user()), 200
        return jsonify(status="error", message="Order not found or you do not have permission to view it."), 404
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred."), 500

# CREATE a new B2B order
@b2b_order_routes_bp.route('/', methods=['POST'])
@b2b_user_required
def create_b2b_order():
    """
    Create a new B2B order. This might use different logic than public checkout,
    e.g., allowing for Purchase Order numbers or different payment methods.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Invalid JSON body"), 400

    sanitized_data = sanitize_input(data)
    
    # Example fields for a B2B order
    required_fields = ['items', 'shipping_address_id', 'purchase_order']
    if not all(field in sanitized_data for field in required_fields):
        missing = [f for f in required_fields if f not in sanitized_data]
        return jsonify(status="error", message=f"Missing required fields: {', '.join(missing)}"), 400

    try:
        # The service would handle creating the order from a list of items rather than a cart.
        order = B2BService.create_b2b_order(user_id, sanitized_data)
        return jsonify(status="success", message="B2B order created successfully.", data=order.to_dict_for_user()), 201
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An error occurred while creating the order."), 500
