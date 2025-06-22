from flask import Blueprint, request, jsonify, g
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

def create_order():
    """Creates a new order with a 'pending_payment' status."""
    user_id = g.user['id']
    data = request.get_json()
    cart_id = data.get('cartId')
    shipping_address = data.get('shippingAddress')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        conn.begin()

        # 1. Re-validate stock for all cart items, locking the rows.
        cursor.execute('SELECT product_id, quantity FROM cart_items WHERE cart_id = %s', (cart_id,))
        cart_items = cursor.fetchall()
        for item in cart_items:
            cursor.execute('SELECT inventory_count FROM products WHERE id = %s FOR UPDATE', (item['product_id'],))
            product = cursor.fetchone()
            if product['inventory_count'] < item['quantity']:
                conn.rollback()
                return jsonify({'error': f"Insufficient stock for product {item['product_id']}"}), 409

        # 2. Create the order.
        order_total = calculate_total(cart_items) # Assumed function
        cursor.execute('INSERT INTO orders (user_id, total, status, shipping_address) VALUES (%s, %s, "pending_payment", %s)',
                       (user_id, order_total, shipping_address))
        order_id = cursor.lastrowid

        # 3. Move items from cart to order_items.
        cursor.execute('INSERT INTO order_items (order_id, product_id, quantity) SELECT %s, product_id, quantity FROM cart_items WHERE cart_id = %s',
                       (order_id, cart_id))

        # 4. Soft-delete the cart.
        cursor.execute('UPDATE carts SET deleted_at = NOW() WHERE id = %s', (cart_id,))
        
        conn.commit()
        
        # 6. Initiate payment session and return details to frontend.
        payment_session = payment_gateway.create_session(order_id, order_total)
        return jsonify({'orderId': order_id, 'paymentSession': payment_session}), 201

    except Exception as e:
        conn.rollback()
        logger.error({'message': 'Order creation failed', 'error': str(e), 'userId': user_id, 'cartId': cart_id})
        return jsonify({'error': 'Internal server error during order creation.'}), 500
    finally:
        cursor.close()
        conn.close()
