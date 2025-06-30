from flask import Blueprint, request, jsonify
from flask_login import current_user 
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.order_service import OrderService
from backend.utils.input_sanitizer import InputSanitizer
from backend.services.cart_service import CartService
from backend.utils.decorators import login_required
from backend.services.exceptions import ServiceError
from backend.services.email_service import EmailService
from backend.schemas import OrderSchema

orders_bp = Blueprint('orders_bp', __name__, url_prefix='/api/orders')

@orders_bp.route('/<int:order_id>', methods=['GET'])
@login_required
def get_order_details(order_id):
    """
    Get details for a specific order.
    This endpoint is now protected against IDOR by filtering on the current_user's ID.
    """
    # By filtering on both order_id and current_user.id, we ensure
    # users can only see their own orders. An attacker cannot guess order IDs
    # to view data belonging to other users.
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()
    
    if not order:
        return jsonify({"error": "Order not found or you do not have permission to view it."}), 404
        
    # Assuming the Order model has a method to serialize its data
    return jsonify(order.to_dict())

@orders_bp.route('/', methods=['GET'])
@login_required
def get_user_orders():
    """
    Get all orders for the currently logged-in user.
    """
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return jsonify([order.to_dict() for order in orders])


def get_session_id():
    """
    Placeholder for getting a unique session ID for anonymous users.
    In a real app, this would likely come from a session cookie.
    """
    return request.headers.get('X-Session-ID')

@orders_bp.route('/create/guest', methods=['POST'])
def create_guest_order():
    """
    Creates an order for a guest user.
    """
    data = request.get_json()
    try:
        order = OrderService.create_guest_order(data)
        return jsonify(OrderSchema().dump(order)), 201
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status_code
    except Exception as e:
        # Proper logging should be here
        return jsonify({"error": "An internal error occurred"}), 500

@orders_bp.route('/create', methods=['POST'])
@login_required
def create_authenticated_order():
    """
    Creates an order for an authenticated user.
    """
    data = request.get_json()
    try:
        order = OrderService.create_authenticated_order(current_user.id, data)
        EmailService.send_order_confirmation_email(order)
        return jsonify(OrderSchema().dump(order)), 201
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status_code

@orders_bp.route('/checkout', methods=['POST'])
@jwt_required(optional=True)
def checkout():
    """
    Handles the entire checkout process. Creates an order from the user's cart.
    Works for both authenticated and anonymous users.
    """
    user_id = get_jwt_identity()
    session_id = get_session_id() if not user_id else None

    if not user_id and not session_id:
        return jsonify(status="error", message="A session is required to check out."), 401

    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Invalid JSON body"), 400
    
    sanitized_data = InputSanitizer.sanitize_input(data)

    required_fields = ['shipping_address', 'billing_address', 'payment_token']
    if not all(field in sanitized_data for field in required_fields):
        missing = [f for f in required_fields if f not in sanitized_data]
        return jsonify(status="error", message=f"Missing required fields: {', '.join(missing)}"), 400

    try:
        # 1. Get the cart
        if user_id:
            cart = CartService.get_cart_by_user_id(user_id)
        else:
            cart = CartService.get_cart_by_session_id(session_id)
        
        if not cart or not cart.items:
            return jsonify(status="error", message="Your cart is empty."), 400

        # 2. Process the order
        # The OrderService should encapsulate all logic:
        # - Verifying inventory
        # - Processing payment via the payment_token (e.g., with Stripe, Adyen)
        # - Creating the order and order items in the database
        # - Clearing the cart
        # - Sending a confirmation email
        order = OrderService.create_order_from_cart(
            cart=cart,
            user_id=user_id,
            checkout_data=sanitized_data
        )
        
        return jsonify(status="success", message="Order placed successfully!", data=order.to_dict_for_user()), 201

    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An unexpected error occurred during checkout."), 500


