from flask import Blueprint, request, jsonify
from backend.services.order_service import OrderService
from backend.services.cart_service import CartService
from backend.services.exceptions import ServiceException, NotFoundException
from flask_jwt_extended import jwt_required, get_jwt_identity

orders_bp = Blueprint('public_order_routes', __name__)

@orders_bp.route('/checkout/create-payment-intent', methods=['POST'])
@jwt_required()
def create_payment_intent():
    """
    Creates a Stripe Payment Intent for the user's cart.
    """
    user_id = get_jwt_identity()
    try:
        # Calculate amount from the server-side cart to prevent manipulation
        cart_total = CartService.get_cart_total(user_id)
        if cart_total == 0:
            return jsonify({"error": "Cart is empty."}), 400
            
        client_secret = OrderService.create_payment_intent(amount=cart_total)
        return jsonify({'clientSecret': client_secret})
    except ServiceException as e:
        return jsonify(error=str(e)), 400

@orders_bp.route('/', methods=['POST'])
@jwt_required()
def create_order():
    """
    Creates an order after a successful payment.
    The frontend provides the payment_intent_id for server-side verification.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    shipping_address = data.get('shipping_address')
    payment_intent_id = data.get('payment_intent_id')

    if not shipping_address or not payment_intent_id:
        return jsonify({"error": "Shipping address and payment intent ID are required."}), 400

    try:
        order = OrderService.create_order_from_cart(user_id, shipping_address, payment_intent_id)
        return jsonify(order.to_dict()), 201
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except ServiceException as e:
        return jsonify({"error": str(e)}), 400
