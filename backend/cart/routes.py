import logging
from flask import Blueprint, g, jsonify, request
from flask_login import current_user, login_required
from marshmallow import ValidationError

from backend.models import CartItem
from backend.schemas import AddToCartSchema, CartItemUpdateSchema, CartSchema
from backend.services.cart_service import CartService
from backend.services.exceptions import (
    NotFoundException,
    ServiceError,
)
from backend.utils.decorators import api_resource_handler

# --- Blueprint and Service Initialization ---
cart_bp = Blueprint("cart_bp", __name__, url_prefix="/api/cart")
logger = logging.getLogger(__name__)
cart_service = CartService(logger)


# --- Cart Routes ---
@cart_bp.route("/", methods=["GET"])
@login_required
def get_cart_contents():
    """
    Gets the contents of the user's cart, with B2B pricing applied if applicable.
    """
    try:
        cart_data = cart_service.get_cart(current_user.id)
        if not cart_data or not cart_data.get("items_details"):
            return (
                jsonify(
                    {
                        "message": "Cart is empty",
                        "items": [],
                        "total": "0.00",
                        "subtotal": "0.00",
                        "discount_applied": "0.00",
                        "tier_name": None,
                    }
                ),
                200,
            )

        return (
            jsonify(
                {
                    "items": [
                        {
                            "item_id": detail["item"].id,
                            "product_id": detail["item"].product.id,
                            "name": detail["item"].product.name,
                            "quantity": detail["item"].quantity,
                            "original_price": str(detail["original_price"]),
                            "discounted_price": str(detail["discounted_price"]),
                            "line_total": str(detail["line_total"]),
                        }
                        for detail in cart_data["items_details"]
                    ],
                    "subtotal": str(cart_data["subtotal"]),
                    "discount_applied": str(cart_data["discount_applied"]),
                    "total": str(cart_data["total"]),
                    "tier_name": cart_data["tier_name"],
                }
            ),
            200,
        )
    except NotFoundException as e:
        return jsonify({"message": str(e)}), 404


@cart_bp.route("/add", methods=["POST"])
@login_required
def add_to_cart():
    """Adds an item to the cart."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "Invalid JSON data provided"}), 400

    # Validate input using marshmallow schema
    try:
        schema = AddToCartSchema()
        validated_data = schema.load(json_data)
    except ValidationError as err:
        return jsonify({"message": "Validation failed", "errors": err.messages}), 400

    try:
        cart_service.add_to_cart(
            current_user.id, validated_data["product_id"], validated_data["quantity"]
        )
        return jsonify({"message": "Item added to cart"}), 201
    except NotFoundException:
        return jsonify({"message": "Product not found"}), 404
    except (ValueError, ServiceError) as e:
        return jsonify({"message": str(e)}), 400


@cart_bp.route("/item/<int:item_id>", methods=["PUT"])
@login_required
@api_resource_handler(
    model=CartItem,
    request_schema=CartItemUpdateSchema,
    response_schema=CartSchema,
)
def update_cart_item_route(instance, validated_data):
    """
    Updates the quantity of an item in the cart.
    """
    updated_cart = cart_service.update_item_quantity(
        user_id=current_user.id,
        item_id=instance.id,
        new_quantity=validated_data["quantity"],
    )
    return updated_cart


@cart_bp.route("/item/<int:item_id>", methods=["DELETE"])
@login_required
@api_resource_handler(model=CartItem, response_schema=CartSchema)
def remove_cart_item_route(instance):
    """Removes a specific item from the cart."""
    updated_cart = cart_service.remove_item(
        user_id=current_user.id, item_id=instance.id
    )
    return updated_cart
