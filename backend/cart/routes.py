from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from backend.services.cart_service import CartService
from backend.utils.input_sanitizer import InputSanitizer
from ..services.loyalty_service import LoyaltyService
from backend.services.exceptions import NotFoundException, ValidationException

cart_bp = Blueprint('cart_bp', __name__, url_prefix='/api/cart')


@cart_bp.route('/add-reward', methods=['POST'])
@jwt_required()
def add_reward_to_cart():
    """Adds a redeemed loyalty reward product to the cart."""
    user_id = get_jwt_identity()
    data = request.get_json()
    reward_id = data.get('reward_id')

    try:
        # First, redeem the points
        success, message = LoyaltyService.redeem_exclusive_reward(user_id, reward_id)
        if not success:
            raise ValidationException(message)
        
        # If points were successfully redeemed, add the item to the cart
        cart = CartService.add_reward_to_cart(user_id, reward_id)
        return jsonify(cart.to_dict())
    except (ValidationException, NotFoundException) as e:
        # If adding to cart fails, we should ideally refund the points.
        # This requires careful transaction management. For now, we return an error.
        LoyaltyService.refund_points_for_reward(user_id, reward_id) # Assumes this method exists
        return jsonify(error=str(e)), 400


def get_session_id():
    """
    Placeholder for getting a unique session ID for anonymous users.
    In a real app, this would likely come from a session cookie.
    """
    # For demonstration, we'll use a header, but a session cookie is better.
    return request.headers.get('X-Session-ID')




@cart_bp.route('/', methods=['GET'])
@login_required
def get_cart_contents():
    """
    Gets the contents of the user's cart, with B2B pricing applied if applicable.
    """
    try:
        cart_data = CartService.get_cart(current_user.id)
        if not cart_data:
            return jsonify({'message': 'Cart is empty', 'items': [], 'total': 0}), 200

        return jsonify({
            'items': [{
                'product_id': detail['item'].product.id,
                'name': detail['item'].product.name,
                'quantity': detail['item'].quantity,
                'original_price': str(detail['original_price']),
                'discounted_price': str(detail['discounted_price']),
                'line_total': str(detail['line_total']),
            } for detail in cart_data['items_details']],
            'subtotal': str(cart_data['subtotal']),
            'discount_applied': str(cart_data['discount_applied']),
            'total': str(cart_data['total']),
            'tier_name': cart_data['tier_name']
        }), 200
    except NotFoundException as e:
        return jsonify({'message': str(e)}), 404

@cart_bp.route('/add', methods=['POST'])
@login_required
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not product_id:
        return jsonify({'message': 'Product ID is required'}), 400
        
    try:
        CartService.add_to_cart(current_user.id, product_id, quantity)
        return jsonify({'message': 'Item added to cart'}), 200
    except NotFoundException:
        return jsonify({'message': 'Product not found'}), 404
    except ValueError as e:
        return jsonify({'message': str(e)}), 400

@cart_bp.route('/remove', methods=['POST'])
@login_required
def remove_from_cart():
    data = request.get_json()
    product_id = data.get('product_id')

    if not product_id:
        return jsonify({'message': 'Product ID is required'}), 400

    CartService.remove_from_cart(current_user.id, product_id)
    return jsonify({'message': 'Item removed from cart'}), 200

@cart_bp.route('/update', methods=['POST'])
@login_required
def update_cart_item():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not product_id or quantity is None:
        return jsonify({'message': 'Product ID and quantity are required'}), 400

    try:
        CartService.update_cart_item_quantity(current_user.id, product_id, quantity)
        return jsonify({'message': 'Cart updated'}), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400




@cart_bp.route('/', methods=['DELETE'])
@jwt_required(optional=True)
def clear_cart():
    """
    Clear all items from the cart.
    """
    user_id = get_jwt_identity()
    session_id = get_session_id() if not user_id else None
    if not user_id and not session_id:
        return jsonify(status="error", message="Authentication or session ID is required."), 401

    try:
        CartService.clear_cart(user_id=user_id, session_id=session_id)
        return jsonify(status="success", message="Cart cleared successfully."), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An error occurred while clearing the cart."), 500

