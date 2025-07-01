from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from backend.services.wishlist_service import WishlistService
from backend.utils.input_sanitizer import InputSanitizer
from backend.utils.decorators import api_resource_handler
from backend.schemas import AddToWishlistSchema, WishlistItemSchema # Added WishlistItemSchema
from backend.models.product_models import Product
from backend.models import WishlistItem # Explicitly import WishlistItem model from models/__init__.py, or define it fully here if it's a standalone model

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
        return jsonify(status="success", data=[item for item in wishlist_items]), 200 # wishlist_items are already dicts from service
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal error occurred while fetching your wishlist."), 500

# ADD an item to the user's wishlist
@wishlist_bp.route('/item', methods=['POST'])
# @api_resource_handler(Product, schema=AddToWishlistSchema()) # Old usage
@jwt_required()
@api_resource_handler( # Apply decorator here
    model=Product, # The target resource for adding to wishlist is Product
    request_schema=AddToWishlistSchema,
    response_schema=WishlistItemSchema, # To serialize the created wishlist item
    ownership_exempt_roles=[], # User adding to their own wishlist, no other roles exempt
    cache_timeout=0, # No caching for user-specific updates
    # check_ownership=True # Not directly applicable as user is creating *their own* wishlist item (implicitly owned)
)
def add_to_wishlist():
    """
    Add a product to the current user's wishlist.
    """
    user_id = get_jwt_identity()
    product_id = g.validated_data['product_id']

    try:
        wishlist_item_data = WishlistService.add_to_wishlist(user_id, product_id)
        # The service returns a dict, so the decorator expects the model instance to serialize.
        # If the service returns a dict representation, we can just jsonify it directly.
        # Given that WishlistService.add_to_wishlist returns a dict, we will keep the direct jsonify.
        # Reverting to direct jsonify unless service layer is changed to return model instance.
        if wishlist_item_data:
            return jsonify(status="success", data=wishlist_item_data), 201
        else:
            return jsonify(status="success", message="Item is already in your wishlist."), 200
    except ValueError as e: # Catches "Product not found" from service
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
