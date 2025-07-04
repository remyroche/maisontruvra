# backend/api/checkout_routes.py
import logging

from flask import Blueprint, current_app, g, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_login import current_user
from marshmallow import ValidationError

from backend.extensions import db
from backend.models.address_models import Address
from backend.models.enums import UserType
from backend.schemas import AddressSchema, ApplyDiscountSchema, CheckoutSchema
from backend.services.cart_service import get_cart_by_id_or_session
from backend.services.checkout_service import (
    CheckoutService,
    process_b2b_checkout,
    process_guest_checkout,
    process_user_checkout,
)
from backend.services.exceptions import (
    AuthorizationException,
    DiscountInvalidException,
    NotFoundException,
)
from backend.services.inventory_service import InventoryService
from backend.services.loyalty_service import LoyaltyService
from backend.utils.decorators import login_required

from ..services.discount_service import DiscountService
from ..utils.decorators import api_resource_handler, roles_required

logger = logging.getLogger(__name__)


checkout_bp = Blueprint("checkout_bp", __name__, url_prefix="/api")
checkout_service = CheckoutService()
discount_service = DiscountService()


class CheckoutService:
    def __init__(self):
        self.inventory_service = InventoryService()
        self.loyalty_service = LoyaltyService()

    @checkout_bp.route("/start", methods=["POST"])
    @login_required
    def start_checkout():
        """
        Validates the structure of the checkout request and initiates the process.
        """
        schema = CheckoutSchema()
        try:
            # This validates that the required IDs are present in the request
            data = schema.load(request.json)
        except ValidationError as err:
            return jsonify(err.messages), 400

        checkout_service = CheckoutService()
        try:
            order = checkout_service.process_checkout(current_user.id, data)
            return jsonify(
                {"message": "Checkout successful!", "order_id": order.id}
            ), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception:
            # Log the full error for debugging
            # current_app.logger.error(f"Checkout failed: {e}", exc_info=True)
            return jsonify(
                {"error": "An unexpected error occurred during checkout."}
            ), 500

    @checkout_bp.route("/", methods=["POST"])
    def checkout():
        """
        Handles the checkout process.
        It differentiates between guest, authenticated B2C, and B2B users.
        """
        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "Invalid JSON data provided."}), 400

        # Validate input using marshmallow schema
        try:
            schema = CheckoutSchema()
            validated_data = schema.load(json_data)
        except ValidationError as err:
            return jsonify({"error": "Validation failed.", "errors": err.messages}), 400

        cart_id = validated_data["cart_id"]
        payment_token = validated_data.get("payment_token")  # e.g., from Stripe.js

        cart = get_cart_by_id_or_session(cart_id)
        if not cart or not cart.items:
            return jsonify({"error": "Your cart is empty or could not be found."}), 400

        order = None
        try:
            if current_user.is_authenticated:
                if (
                    hasattr(current_user, "user_type")
                    and current_user.user_type == UserType.B2B
                ):
                    # B2B checkout process
                    payment_details = validated_data.get(
                        "payment_details"
                    )  # Could be PO number, etc.
                    order = process_b2b_checkout(current_user, cart, payment_details)
                else:
                    # Regular B2C user checkout
                    order = process_user_checkout(current_user, cart, payment_token)
            else:
                # Guest checkout
                guest_data = validated_data.get("guest_info")
                if not guest_data or not guest_data.get("email"):
                    return jsonify(
                        {"error": "Guest information and email are required."}
                    ), 400
                order = process_guest_checkout(guest_data, cart, payment_token)

            if order:
                return jsonify({"status": "success", "order_id": order.id}), 200
            else:
                # This case handles scenarios where order creation fails in the service layer
                return jsonify(
                    {
                        "error": "Checkout failed. Please review your order details and try again."
                    }
                ), 400

        except Exception as e:
            current_app.logger.error(f"Checkout process failed: {e}", exc_info=True)
            return jsonify(
                {
                    "error": "An unexpected error occurred during checkout. Please try again later."
                }
            ), 500

    @checkout_bp.route("/session", methods=["GET"])
    def get_checkout_session():
        """
        Gets all necessary data for the checkout page, now including available discounts.
        """
        user = g.get("user", None)
        checkout_data = checkout_service.get_checkout_data(user)

        # --- New Addition: Get available discounts for the logged-in user ---
        if user:
            checkout_data["available_discounts"] = (
                discount_service.get_available_discounts_for_user(user)
            )
        else:
            checkout_data["available_discounts"] = []

        return jsonify(checkout_data)

    @checkout_bp.route("/apply-discount", methods=["POST"])
    @roles_required("Admin", "Manager")
    def apply_discount():
        """Endpoint for the user to apply a discount code to their cart."""
        user = g.get("user")
        if not user:
            return jsonify({"error": "You must be logged in to apply a discount."}), 401

        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "Invalid JSON data provided."}), 400

        # Validate input using marshmallow schema
        try:
            schema = ApplyDiscountSchema()
            validated_data = schema.load(json_data)
        except ValidationError as err:
            return jsonify({"error": "Validation failed.", "errors": err.messages}), 400

        cart = checkout_service.get_user_cart(user.id)  # Assuming a method to get cart
        if not cart:
            return jsonify({"error": "Cart not found."}), 404

        try:
            result = discount_service.apply_discount_code(
                cart, user, validated_data["code"]
            )
            return jsonify(result)
        except DiscountInvalidException as e:
            return jsonify({"error": str(e)}), 400

    @checkout_bp.route("/user/addresses", methods=["GET"])
    @jwt_required()
    def get_user_addresses():
        """Fetches all addresses for the currently authenticated user."""
        user_id = get_jwt_identity()
        try:
            addresses = CheckoutService.get_user_addresses(user_id)
            return jsonify(addresses=[address.to_dict() for address in addresses])
        except NotFoundException as e:
            return jsonify(error=str(e)), 404

    @checkout_bp.route("/user/addresses", methods=["POST"])
    @api_resource_handler(
        model=Address,
        request_schema=AddressSchema,
        response_schema=AddressSchema,
        ownership_exempt_roles=[],  # Only the user themselves can create
        cache_timeout=0,  # No caching for addresses
        log_action=True,
    )
    @jwt_required()
    def add_user_address():
        """Adds a new address for the currently authenticated user."""
        user_id = get_jwt_identity()

        # Create new address with validated data
        address = Address()
        address.user_id = user_id
        for key, value in g.validated_data.items():
            if hasattr(address, key):
                setattr(address, key, value)

        db.session.add(address)
        return address

    @checkout_bp.route("/user/addresses/<int:address_id>", methods=["PUT"])
    @api_resource_handler(
        model=Address,
        request_schema=AddressSchema,
        response_schema=AddressSchema,
        ownership_exempt_roles=[],  # Only the owner can update
        cache_timeout=0,  # No caching for addresses
        log_action=True,
    )
    @jwt_required()
    def update_user_address(address_id):
        """Updates an existing address for the currently authenticated user."""
        user_id = get_jwt_identity()

        # Address is already fetched and validated by decorator
        address = g.target_object

        # Verify ownership
        if address.user_id != user_id:
            raise AuthorizationException(
                "You do not have permission to update this address."
            )

        # Update address with validated data
        for key, value in g.validated_data.items():
            if hasattr(address, key):
                setattr(address, key, value)

        return address

    @checkout_bp.route("/delivery/methods", methods=["GET"])
    def get_delivery_methods():
        """Gets available delivery methods based on address and cart total."""
        # In a real app, you'd pass address and cart data from request.args
        # For now, we fetch all available methods.
        methods = CheckoutService.get_available_delivery_methods(
            address={}, cart_total=0
        )
        return jsonify(delivery_methods=[method.to_dict() for method in methods])

    @checkout_bp.route("/delivery/methods", methods=["GET"])
    @jwt_required()
    def _dispatch_post_order_tasks(self, order, user, points_earned):
        """
        Helper method to dispatch all asynchronous post-order tasks.
        This is where we import tasks to avoid circular dependencies.
        """
        try:
            # --- THIS IS THE KEY FIX ---
            # Import tasks here, inside the method, not at the top of the file.
            from backend.tasks import (
                notify_admin_of_new_order_task,
                notify_user_of_loyalty_points_task,  # This now exists and can be imported
                send_order_confirmation_email_task,
                update_inventory_on_order_task,
            )

            # Dispatch tasks
            send_order_confirmation_email_task.delay(order.id)
            notify_admin_of_new_order_task.delay(order.id)

            # Assuming order.items exists and is iterable
            for item in order.items:
                update_inventory_on_order_task.delay(item.product_id, item.quantity)

            if user and points_earned > 0:
                notify_user_of_loyalty_points_task.delay(user.id, points_earned)

        except ImportError as e:
            logger.critical(
                f"CRITICAL: Could not import Celery tasks for post-order processing: {e}",
                exc_info=True,
            )
        except Exception as e:
            logger.error(
                f"Failed to dispatch post-order tasks for order {order.id}: {e}",
                exc_info=True,
            )
