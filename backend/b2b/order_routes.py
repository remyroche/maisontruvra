import logging

from flask import Blueprint, g, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.models.order_models import Order
from backend.schemas import B2BOrderCreationSchema, OrderSchema
from backend.services.b2b_service import B2BService
from backend.services.exceptions import ValidationException
from backend.utils.decorators import api_resource_handler

# --- Blueprint and Service Initialization ---
b2b_order_bp = Blueprint("b2b_order_bp", __name__, url_prefix="/api/b2b/orders")
logger = logging.getLogger(__name__)
b2b_service = B2BService(logger)


@b2b_order_bp.route("/", methods=["POST"])
@jwt_required()
@api_resource_handler(
    model=Order,
    request_schema=B2BOrderCreationSchema,
    response_schema=OrderSchema,
    log_action=True,
)
def create_b2b_order():
    """
    Creates a new B2B order.
    The decorator handles input validation and response serialization.
    The service call is retained to perform complex business logic.
    """
    user_id = get_jwt_identity()
    new_order = B2BService.create_order(user_id, g.validated_data)
    return new_order


@order_routes.route("/orders", methods=["GET"])
@permissions_required("MANAGE_ORDERS")
@roles_required("Admin", "Manager", "Support")
def list_all_orders():
    """
    Retrieves a paginated list of all customer orders.
    C[R]UD - Read (List)
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    status_filter = InputSanitizer.sanitize_input(request.args.get("status"))

    query = Order.query.options(joinedload(Order.user)).order_by(
        Order.created_at.desc()
    )

    if status_filter:
        query = query.filter(Order.status == status_filter)

    orders_page = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(
        {
            "orders": [order.to_admin_dict() for order in orders_page.items],
            "total": orders_page.total,
            "page": orders_page.page,
            "pages": orders_page.pages,
        }
    )


@order_routes.route("/<int:order_id>", methods=["GET"])
@api_resource_handler(
    model=Order,
    response_schema=OrderSchema,
    ownership_exempt_roles=["Admin", "Manager", "Support"],  # Staff can view all orders
    eager_loads=["items", "user", "shipping_address"],  # Eager load order details
    cache_timeout=300,  # 5 minute cache for order details
    log_action=True,  # Log order access
)
@permissions_required("MANAGE_ORDERS")
@roles_required("Admin", "Manager", "Support")
def get_order_details(order_id):
    """
    Retrieves details for a specific order.
    """
    # Order is already fetched and validated by decorator
    return g.target_object


@order_routes.route("/<int:order_id>/status", methods=["PUT"])
@api_resource_handler(
    model=Order,
    request_schema=OrderStatusUpdateSchema,
    response_schema=OrderSchema,
    ownership_exempt_roles=[
        "Admin",
        "Manager",
        "Support",
    ],  # Staff can update all orders
    cache_timeout=0,  # No caching for status updates
    log_action=True,  # Log status changes
)
@permissions_required("MANAGE_ORDERS")
@roles_required("Admin", "Manager", "Support")
def update_order_status(order_id):
    """
    Updates the status of a specific order.
    """
    # Order is already fetched and validated by decorator

    # Update order status using the service layer
    try:
        updated_order = OrderService.update_order_status(
            order_id, g.validated_data["status"]
        )
        if not updated_order:
            raise NotFoundException("Order not found")

        # Return the updated order (decorator will handle serialization)
        return updated_order
    except ValueError as e:
        raise ValidationException(str(e))


@order_routes.route("/", methods=["GET"])
@permissions_required("MANAGE_ORDERS")
@roles_required("Admin", "Manager", "Support")
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
    status = request.args.get("status")
    user_id = request.args.get("user_id")
    include_deleted = request.args.get("include_deleted", "false").lower() == "true"
    orders = OrderService.get_all_orders(
        status=status, user_id=user_id, include_deleted=include_deleted
    )
    return jsonify([order.to_dict() for order in orders])


# DELETE an order
@order_routes.route("/<int:order_id>", methods=["DELETE"])
@api_resource_handler(
    model=Order,
    ownership_exempt_roles=["Admin", "Manager"],  # Only Admin/Manager can delete orders
    cache_timeout=0,  # No caching for delete operations
    allow_hard_delete=True,  # Allow hard delete for orders
    log_action=True,  # Log order deletions
)
@permissions_required("MANAGE_ORDERS")
@roles_required("Admin", "Manager")  # More restrictive for deletion
def delete_order(order_id, is_hard_delete=False):
    """
    Delete an order. This should be used with caution.
    """
    # Order is already fetched and validated by decorator
    order = g.target_object

    if is_hard_delete:
        # Hard delete - permanently remove from database
        db.session.delete(order)
    else:
        # Soft delete - mark as deleted
        if hasattr(order, "deleted_at"):
            from datetime import datetime

            order.deleted_at = datetime.utcnow()
        else:
            # If no soft delete field, use service layer
            OrderService.soft_delete_order(order_id)

    return None  # Decorator will handle the delete response


@order_routes.route("/<int:order_id>/restore", methods=["PUT"])
@api_resource_handler(
    model=Order,
    response_schema=OrderSchema,
    ownership_exempt_roles=["Admin", "Manager", "Support"],  # Staff can restore orders
    cache_timeout=0,  # No caching for restore operations
    log_action=True,  # Log order restorations
)
@permissions_required("MANAGE_ORDERS")
@roles_required("Admin", "Manager", "Support")
def restore_order(order_id):
    """
    Restore a soft-deleted order.
    """
    # Order is already fetched and validated by decorator
    order = g.target_object

    # Restore the order
    if hasattr(order, "deleted_at"):
        order.deleted_at = None
    else:
        # Use service layer if no direct field
        OrderService.restore_order(order_id)

    return order
