"""
This module defines the API endpoints for order management in the admin panel.
It uses the @api_resource_handler for secure and consistent handling of single
order operations and provides a separate endpoint for paginated listing.
"""

from flask import Blueprint, g, jsonify, request

from ..models import Order
from ..schemas import OrderSchema, OrderUpdateSchema
from ..services.order_service import OrderService
from ..utils.decorators import api_resource_handler, roles_required

# --- Blueprint Setup ---
bp = Blueprint("order_management", __name__, url_prefix="/api/admin/orders")


@bp.route("/", methods=["GET"])
@roles_required("Admin", "Manager")
def list_orders():
    """
    Handles listing and pagination of all orders. This is a collection-level
    operation and is handled separately from the single-resource decorator.
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    status_filter = request.args.get("status", None, type=str)

    filters = {}
    if status_filter:
        filters["status"] = status_filter

    paginated_orders = OrderService.get_all_orders_paginated(
        page=page, per_page=per_page, filters=filters
    )

    return jsonify(
        {
            "data": OrderSchema(many=True).dump(paginated_orders.items),
            "total": paginated_orders.total,
            "pages": paginated_orders.pages,
            "current_page": paginated_orders.page,
        }
    )


@bp.route("/<int:order_id>", methods=["GET", "PUT"])
@roles_required("Admin", "Manager")
@api_resource_handler(
    model=Order,
    request_schema=OrderUpdateSchema,  # For validating PUT data
    response_schema=OrderSchema,  # For serializing GET response
    eager_loads=["user", "shipping_address", "items"],  # Performance boost
    log_action=True,
    cache_timeout=600,
)
def handle_single_order(order_id):
    """
    Handles viewing and updating a single order.
    The decorator manages fetching, validation, transactions, and caching.
    """
    if request.method == "GET":
        # The decorator has fetched the order and placed it in g.target_object.
        # We just need to return it for automatic serialization.
        return g.target_object

    elif request.method == "PUT":
        # The decorator has fetched the order (g.target_object) and
        # validated the incoming data (g.validated_data).
        order_to_update = g.target_object
        update_data = g.validated_data

        return OrderService.update_order_status(order_to_update, update_data)
