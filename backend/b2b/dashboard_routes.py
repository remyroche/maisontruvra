from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

# from backend.utils.decorators import api_resource_handler # Not using it currently for these routes
from backend.schemas import AddToWishlistSchema
from backend.services.wishlist_service import WishlistService

# Assuming WishlistItem is properly imported or defined elsewhere and accessible via models.__init__
# If WishlistItem is strictly within wishlist_service.py as a local class, it cannot be used as a model for decorators directly.
# However, the schemas.py imports it as `from .models.product_models import Product, Variant, WishlistItem`.
# This implies it should be moved to a proper models file if not already.
# For now, let's assume `backend.models.product_models.WishlistItem` is the correct path.

wishlist_bp = Blueprint("wishlist_bp", __name__, url_prefix="/api/wishlist")


# READ the current user's wishlist
@wishlist_bp.route("/", methods=["GET"])
@jwt_required()
def get_wishlist():
    """
    Get all items in the current user's wishlist.
    """
    user_id = get_jwt_identity()
    try:
        wishlist_items = WishlistService.get_wishlist_items(user_id)
        # WishlistService.get_wishlist_items already returns list of dicts, so no .to_dict() needed here
        return jsonify(status="success", data=wishlist_items), 200
    except Exception:
        # Log error e
        return jsonify(
            status="error",
            message="An internal error occurred while fetching your wishlist.",
        ), 500


# ADD an item to the user's wishlist
@wishlist_bp.route("/item", methods=["POST"])
@jwt_required()
# Keeping as manual due to service returning dict and complex ownership for future @api_resource_handler
def add_to_wishlist():
    """
    Add a product to the current user's wishlist.
    """
    user_id = get_jwt_identity()
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Invalid JSON data provided"}), 400

    try:
        # Manually validate input using marshmallow schema
        schema = AddToWishlistSchema()
        validated_data = schema.load(json_data)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "errors": err.messages}), 400

    product_id = validated_data["product_id"]

    try:
        wishlist_item_data = WishlistService.add_to_wishlist(user_id, product_id)
        if wishlist_item_data:
            return jsonify(status="success", data=wishlist_item_data), 201
        else:
            # This case handles if the item was already in the wishlist (service might return None or raise exception)
            # Based on service code, it raises ValidationException, which is caught below
            return jsonify(
                status="success", message="Item is already in your wishlist."
            ), 200
    except ValueError as e:  # Catches "Product not found" from service
        return jsonify(status="error", message=str(e)), 404
    except Exception:
        # Log error e
        return jsonify(status="error", message="An internal error occurred."), 500


# REMOVE an item from the user's wishlist
@wishlist_bp.route("/item/<int:product_id>", methods=["DELETE"])
@jwt_required()
# Keeping as manual due to complex ownership check needing user_id AND product_id
def remove_from_wishlist(product_id):
    """
    Remove a product from the current user's wishlist.
    """
    user_id = get_jwt_identity()
    try:
        if WishlistService.remove_from_wishlist(user_id, product_id):
            return jsonify(status="success", message="Item removed from wishlist."), 200
        else:
            return jsonify(status="error", message="Item not found in wishlist."), 404
    except Exception:
        # Log error e
        return jsonify(status="error", message="An internal error occurred."), 500
