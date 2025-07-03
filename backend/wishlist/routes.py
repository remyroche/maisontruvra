# backend/wishlist/routes.py

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.wishlist_service import WishlistService
from ..services.exceptions import NotFoundException, ValidationException, ServiceError
from backend.utils.decorators import api_resource_handler
from ..models.wishlist_models import WishlistItem # Assuming this is the path
from ..schemas import WishlistItemSchema # Assuming this exists for validation



# Create a Blueprint for wishlist routes
wishlist_bp = Blueprint('wishlist_bp', __name__, url_prefix='/api/wishlist')

@wishlist_bp.route('/', methods=['GET'])
@jwt_required()
def get_wishlist():
    """
    Get the current user's wishlist items.
    """
    user_id = get_jwt_identity()
    try:
        items = WishlistService.get_wishlist_items(user_id)
        return jsonify(items), 200
    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except ServiceError as e:
        return jsonify({'error': str(e)}), 500

@wishlist_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_wishlist():
    """
    Add a product to the current user's wishlist.
    Expects {'product_id': <id>} in the request body.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    product_id = data.get('product_id')

    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400

    try:
        added_item = WishlistService.add_to_wishlist(user_id, product_id)
        return jsonify(added_item), 201
    except (NotFoundException, ValidationException) as e:
        return jsonify({'error': str(e)}), 400
    except ServiceError as e:
        return jsonify({'error': str(e)}), 500

@wishlist_bp.route('/remove/<int:product_id>', methods=['DELETE'])
@jwt_required()
def remove_from_wishlist(product_id):
    """
    Remove a prwishlist_bp = Blueprint('wishlist_bp', __name__, url_prefix='/api')
    """

@wishlist_bp.route('/wishlist', methods=['GET'])
@jwt_required()
def get_wishlist_items_for_user():
    """
    Get the current user's wishlist items.
    """
    user_id = get_jwt_identity()
    try:
        items = WishlistService.get_wishlist_items(user_id)
        return jsonify(items), 200
    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except ServiceError as e:
        return jsonify({'error': str(e)}), 500

@wishlist_bp.route('/wishlist/items', methods=['POST'])
@jwt_required()
@api_resource_handler(model=WishlistItem, request_schema=WishlistItemSchema)
def add_to_wishlist():
    """
    Add a product to the current user's wishlist.
    The decorator handles validation, creation, and response.
    Expects {'product_id': <id>} in the request body.
    """
    user_id = get_jwt_identity()
    # g.validated_data is populated by the decorator
    product_id = g.validated_data.get('product_id')
    
    # The service layer contains the core business logic
    added_item = WishlistService.add_to_wishlist(user_id, product_id)
    # The decorator will serialize this object using the response_schema
    return added_item

@wishlist_bp.route('/wishlist/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
@api_resource_handler(model=WishlistItem, lookup_field='id', ownership_field='user_id', allow_hard_delete=True)
def remove_from_wishlist(item_id):
    """
    Remove a specific item from the current user's wishlist.
    The decorator handles finding the item by its ID, checking ownership
    (ensuring the item's user_id matches the logged-in user), and deleting it.
    The function body is empty because the decorator handles the entire action.
    """
    pass

@wishlist_bp.route('/wishlist/check/<int:product_id>', methods=['GET'])
@jwt_required()
def check_wishlist_item(product_id):
    """
    Check if a specific product is in the user's wishlist.
    """
    user_id = get_jwt_identity()
    try:
        is_in = WishlistService.is_in_wishlist(user_id, product_id)
        return jsonify({'is_in_wishlist': is_in}), 200
    except ServiceError as e:
        return jsonify({'error': str(e)}), 500
