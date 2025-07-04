from flask import Blueprint, current_app, g, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_login import current_user
from marshmallow import ValidationError

from backend.models.order_models import Order
from backend.schemas import (
    AuthenticatedOrderSchema,
    CheckoutOrderSchema,
    GuestOrderSchema,
    OrderSchema,
)
from backend.services.cart_service import CartService
from backend.services.email_service import EmailService
from backend.services.exceptions import AuthorizationException, ServiceError
from backend.services.order_service import OrderService
from backend.utils.decorators import api_resource_handler, login_required

orders_bp = Blueprint("orders_bp", __name__, url_prefix="/api/orders")


@orders_bp.route("/<int:order_id>", methods=["GET"])
@api_resource_handler(
    model=Order,
    response_schema=OrderSchema,
    ownership_exempt_roles=[],  # Only the order owner can view
    eager_loads=["items", "shipping_address"],  # Eager load order details
    cache_timeout=0,  # No caching for user-specific orders
    log_action=True,  # Log order access
)
@login_required
def get_order_details(order_id):
    """
    Get details for a specific order.
    This endpoint is now protected against IDOR by the api_resource_handler decorator.
    """
    # Order is already fetched and validated by decorator
    order = g.target_object

    # Verify ownership
    if order.user_id != current_user.id:
        raise AuthorizationException("You do not have permission to view this order")

    return order


@orders_bp.route("/", methods=["GET"])
@login_required
def get_user_orders():
    """
    Get all orders for the currently logged-in user.
    """
    orders = (
        Order.query.filter_by(user_id=current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return jsonify([order.to_dict() for order in orders])


def get_session_id():
    """
    Placeholder for getting a unique session ID for anonymous users.
    In a real app, this would likely come from a session cookie.
    """
    return request.headers.get("X-Session-ID")


@orders_bp.route("/create/guest", methods=["POST"])
def create_guest_order():
    """
    Creates an order for a guest user.
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Invalid JSON data provided"}), 400

    # Validate input using marshmallow schema
    try:
        schema = GuestOrderSchema()
        validated_data = schema.load(json_data)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "errors": err.messages}), 400

    try:
        order = OrderService.create_guest_order(validated_data)
        return jsonify(OrderSchema().dump(order)), 201
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status_code
    except Exception as e:
        # Proper logging should be here
        current_app.logger.error(f"Error creating guest order: {str(e)}", exc_info=True)
        return jsonify({"error": "An internal error occurred"}), 500


@orders_bp.route("/create", methods=["POST"])
@login_required
def create_authenticated_order():
    """
    Creates an order for an authenticated user.
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Invalid JSON data provided"}), 400

    # Validate input using marshmallow schema
    try:
        schema = AuthenticatedOrderSchema()
        validated_data = schema.load(json_data)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "errors": err.messages}), 400

    try:
        order = OrderService.create_authenticated_order(current_user.id, validated_data)
        EmailService.send_order_confirmation_email(order)
        return jsonify(OrderSchema().dump(order)), 201
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status_code
    except Exception as e:
        current_app.logger.error(
            f"Error creating authenticated order for user {current_user.id}: {str(e)}",
            exc_info=True,
        )
        return jsonify({"error": "An internal error occurred"}), 500


@orders_bp.route("/checkout", methods=["POST"])
@jwt_required(optional=True)
def checkout():
    """
    Handles the entire checkout process. Creates an order from the user's cart.
    Works for both authenticated and anonymous users.
    """
    user_id = get_jwt_identity()
    session_id = get_session_id() if not user_id else None

    if not user_id and not session_id:
        return jsonify(
            status="error", message="A session is required to check out."
        ), 401

    json_data = request.get_json()
    if not json_data:
        return jsonify(status="error", message="Invalid JSON data provided"), 400

    # Validate input using marshmallow schema
    try:
        schema = CheckoutOrderSchema()
        validated_data = schema.load(json_data)
    except ValidationError as err:
        return jsonify(
            status="error", message="Validation failed", errors=err.messages
        ), 400

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
            cart=cart, user_id=user_id, checkout_data=validated_data
        )

        return jsonify(
            status="success",
            message="Order placed successfully!",
            data=order.to_dict_for_user(),
        ), 201

    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log the error e
        current_app.logger.error(
            f"An unexpected error occurred during checkout: {str(e)}", exc_info=True
        )
        return jsonify(
            status="error", message="An unexpected error occurred during checkout."
        ), 500
