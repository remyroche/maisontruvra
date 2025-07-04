from flask import Blueprint, current_user, g, jsonify, request

from backend.models.inventory_models import StockNotification
from backend.schemas import StockNotificationSchema
from backend.services import product_service
from backend.services.inventory_service import InventoryService  # Assumed service
from backend.utils.decorators import (
    admin_required,
    api_resource_handler,
    login_required,
    permissions_required,
)
from backend.utils.input_sanitizer import InputSanitizer

inventory_bp = Blueprint("inventory_bp", __name__, url_prefix="/api/inventory")


@inventory_bp.route("/notify-in-stock", methods=["POST"])
@login_required
@api_resource_handler(
    model=StockNotification,
    request_schema=StockNotificationSchema,
    response_schema=StockNotificationSchema,
    log_action=True,
)
def notify_in_stock():
    """
    Creates a stock notification request for a user and product.
    The decorator handles validation and response serialization.
    """
    notification = InventoryService.create_stock_notification(
        user_id=current_user.id, product_id=g.validated_data.get("product_id")
    )
    return notification


# Check stock level for a specific product
@inventory_bp.route("/stock/<int:product_id>", methods=["GET"])
@permissions_required("VIEW_INVENTORY")
def get_stock_level(product_id):
    """
    Get the current stock level for a specific product.
    Requires permission to view inventory.
    """
    try:
        stock_info = InventoryService.get_stock_for_product(product_id)
        if stock_info is None:
            return jsonify(
                status="error", message="Product not found in inventory."
            ), 404

        return jsonify(status="success", data=stock_info), 200
    except Exception:
        # Log error e
        return jsonify(
            status="error",
            message="An internal error occurred while fetching stock levels.",
        ), 500


@inventory_bp.route("/update", methods=["POST"])
@admin_required
def update_inventory_levels():
    data = InputSanitizer.sanitize_input(request.get_json())
    # data format: [{'product_id': 1, 'quantity': 100}, ...]
    try:
        product_service.update_inventory_levels(data)
        return jsonify({"message": "Inventory levels updated successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
