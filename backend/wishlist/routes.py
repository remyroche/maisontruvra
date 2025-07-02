# Refactoring backend/wishlist/routes.py
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from backend.services.wishlist_service import WishlistService, WishlistItem
from backend.utils.input_sanitizer import InputSanitizer
from backend.utils.decorators import api_resource_handler
from backend.schemas import AddToWishlistSchema, WishlistItemSchema
from backend.models.product_models import Product
from backend.extensions import db
from backend.services.exceptions import NotFoundException, ValidationException, AuthorizationException

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
        # WishlistService.get_wishlist_items already returns list of dicts, so no .to_dict() needed here
        return jsonify(status="success", data=wishlist_items), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal error occurred while fetching your wishlist."), 500

# ADD an item to the user's wishlist
@wishlist_bp.route('/item', methods=['POST'])
@api_resource_handler(
    model=WishlistItem,
    request_schema=AddToWishlistSchema,
    response_schema=WishlistItemSchema,
    ownership_exempt_roles=[],  # Only the user themselves can add to wishlist
    cache_timeout=0,  # No caching for wishlist operations
    log_action=True
)
@jwt_required()
def add_to_wishlist():
    """
    Add a product to the current user's wishlist.
    """
    user_id = get_jwt_identity()
    product_id = g.validated_data['product_id']
    
    # Check if product exists
    product = Product.query.get(product_id)
    if not product:
        raise NotFoundException("Product not found")
    
    # Check if item already exists in wishlist
    existing_item = WishlistItem.query.filter_by(
        user_id=user_id, 
        product_id=product_id
    ).first()
    
    if existing_item:
        raise ValidationException("Item is already in your wishlist")
    
    # Create new wishlist item
    wishlist_item = WishlistItem()
    wishlist_item.user_id = user_id
    wishlist_item.product_id = product_id
    
    db.session.add(wishlist_item)
    return wishlist_item

# REMOVE an item from the user's wishlist
@wishlist_bp.route('/item/<int:product_id>', methods=['DELETE'])
@jwt_required()
def remove_from_wishlist(product_id):
    """
    Remove a product from the current user's wishlist.
    """
    user_id = get_jwt_identity()
    
    # Find the wishlist item by user_id and product_id
    wishlist_item = WishlistItem.query.filter_by(
        user_id=user_id, 
        product_id=product_id
    ).first()
    
    if not wishlist_item:
        raise NotFoundException("Item not found in wishlist")
    
    # Delete the wishlist item
    db.session.delete(wishlist_item)
    db.session.commit()
    
    return jsonify({"message": "Item removed from wishlist successfully"}), 200

# Alternative endpoint using wishlist_item_id for direct access
@wishlist_bp.route('/item/id/<int:item_id>', methods=['DELETE'])
@api_resource_handler(
    model=WishlistItem,
    ownership_exempt_roles=[],  # Only the owner can delete
    cache_timeout=0,  # No caching for wishlist operations
    log_action=True
)
@jwt_required()
def remove_wishlist_item_by_id(item_id):
    """
    Remove a wishlist item by its ID (alternative endpoint).
    """
    # WishlistItem is already fetched and validated by decorator
    wishlist_item = g.target_object
    
    # Verify ownership
    user_id = get_jwt_identity()
    if wishlist_item.user_id != user_id:
        raise AuthorizationException("You do not have permission to delete this wishlist item")
    
    db.session.delete(wishlist_item)
    return None  # Decorator will handle the delete response
