"""
This module defines the API endpoints for delivery method management in the admin panel.
It leverages the @api_resource_handler to create clean, secure, and consistent CRUD endpoints.
"""

from flask import Blueprint, g, get_jwt_identity, jsonify, jwt_required, request

from ..models import DeliveryMethod
from ..schemas import DeliveryMethodSchema
from ..services.delivery_service import DeliveryService
from ..utils.decorators import api_resource_handler, roles_required

# --- Blueprint Setup ---
bp = Blueprint(
    "delivery_management", __name__, url_prefix="/api/admin/delivery-methods"
)


@bp.route("/", methods=["GET", "POST"])
@bp.route("/<int:method_id>", methods=["GET", "PUT", "DELETE"])
@roles_required("Admin", "Manager")
@api_resource_handler(
    model=DeliveryMethod,
    request_schema=DeliveryMethodSchema,
    response_schema=DeliveryMethodSchema,
    log_action=True,
    allow_hard_delete=True,  # Delivery methods can be hard-deleted as they are simple records
)
def handle_delivery_methods(method_id=None, is_hard_delete=False):
    """Handles all CRUD operations for Delivery Methods."""

    # Handle the collection GET request for all delivery methods
    if request.method == "GET" and method_id is None:
        all_methods = DeliveryService.get_all_methods_for_admin()
        return jsonify(DeliveryMethodSchema(many=True).dump(all_methods))

    # --- Single Delivery Method Operations ---
    # The decorator handles fetching the method and validating data.

    if request.method == "GET":
        # g.target_object is the method fetched by the decorator.
        return g.target_object

    elif request.method == "POST":
        # g.validated_data contains the sanitized and validated method data.
        return DeliveryService.create_method(g.validated_data)

    elif request.method == "PUT":
        # g.target_object is the method to update.
        # g.validated_data contains the new data.
        return DeliveryService.update_method(g.target_object, g.validated_data)

    elif request.method == "DELETE":
        # The decorator handles the hard/soft delete logic.
        # Here, we've allowed hard delete, so we just call the service.
        DeliveryService.delete_method(method_id)
        return None  # Decorator provides the success message.


# --- Public-Facing API ---
# Note: This blueprint is not currently registered in backend/__init__.py
delivery_public_bp = Blueprint("delivery_public_bp", __name__)


@delivery_public_bp.route("/", methods=["GET"])
@jwt_required()  # Assuming this is for authenticated B2C/B2B users
def get_public_delivery_methods():
    """Public endpoint for authenticated users to fetch available delivery methods."""
    user_id = get_jwt_identity()
    try:
        methods = DeliveryService.get_available_methods_for_user(user_id)
        return jsonify(status="success", data=methods), 200
    except Exception as e:
        return jsonify(status="error", message=str(e)), 500
