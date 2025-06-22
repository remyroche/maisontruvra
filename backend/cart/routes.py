from flask import Blueprint, request, jsonify
from backend.services.cart_service import CartService
from backend.services.exceptions import ServiceException, NotFoundException
from flask_jwt_extended import jwt_required, get_jwt_identity

cart_bp = Blueprint('cart_bp', __name__)

@cart_bp.route('/', methods=['GET'])
@jwt_required()
def get_cart():
    """
    Get the contents of the current user's cart.
    """
    user_id = get_jwt_identity()
    try:
        cart_items = CartService.get_cart_contents(user_id)
        return jsonify(cart_items), 200
    except ServiceException as e:
        return jsonify({"error": str(e)}), 500

@cart_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    """
    Add an item to the cart.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if not product_id:
        return jsonify({"error": "Product ID is required."}), 400
    
    try:
        item = CartService.add_item_to_cart(user_id, product_id, quantity)
        return jsonify(item.to_dict()), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except ServiceException as e:
        return jsonify({"error": str(e)}), 400

@cart_bp.route('/update/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(item_id):
    """
    Update the quantity of an item in the cart.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    quantity = data.get('quantity')

    if quantity is None:
        return jsonify({"error": "Quantity is required."}), 400
        
    try:
        item = CartService.update_cart_item_quantity(user_id, item_id, quantity)
        return jsonify(item.to_dict()), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except ServiceException as e:
        return jsonify({"error": str(e)}), 400

@cart_bp.route('/remove/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    """
    Remove an item from the cart.
    """
    user_id = get_jwt_identity()
    try:
        CartService.remove_item_from_cart(user_id, item_id)
        return jsonify({"message": "Item removed successfully"}), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except ServiceException as e:
        return jsonify({"error": str(e)}), 500