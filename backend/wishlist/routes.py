from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.wishlist_service import WishlistService
from backend.utils.sanitization import sanitize_input

wishlist_bp = Blueprint('wishlist_bp', __name__, url_prefix='/api/wishlist')

# READ the current user's wishlist
@wishlist_bp.route('/', methods=['GET'])
@jwt_required()
def get_wishlist():
    """
    Get all items in the current user's wishlist.
    """
    user_id = get_jwt_identity()
    try:
        wishlist_items = WishlistService.get_wishlist_items(user_id)
        return jsonify(status="success", data=[item.to_dict() for item in wishlist_items]), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal error occurred while fetching your wishlist."), 500

# ADD an item to the user's wishlist
@wishlist_bp.route('/item', methods=['POST'])
@jwt_required()
def add_to_wishlist():
    """
    Add a product to the current user's wishlist.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data or 'product_id' not in data:
        return jsonify(status="error", message="product_id is required."), 400

    try:
        product_id = int(sanitize_input(data['product_id']))
        wishlist_item = WishlistService.add_to_wishlist(user_id, product_id)
        if wishlist_item:
            return jsonify(status="success", data=wishlist_item.to_dict()), 201
        else:
            # This case handles if the item was already in the wishlist
            return jsonify(status="success", message="Item is already in your wishlist."), 200
    except ValueError as e: # Catches "Product not found"
        return jsonify(status="error", message=str(e)), 404
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal error occurred."), 500

# REMOVE an item from the user's wishlist
@wishlist_bp.route('/item/<int:product_id>', methods=['DELETE'])
@jwt_required()
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
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal error occurred."), 500
