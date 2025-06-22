from flask import Blueprint, request, jsonify
from backend.services.cart_service import CartService
from backend.services.exceptions import ServiceException, NotFoundException
from flask_jwt_extended import jwt_required, get_jwt_identity

cart_bp = Blueprint('cart_bp', __name__)

@cart_bp.route('/cart/items', methods=['POST'])
@permission_required() # Replaced auth_required with the new permission decorator
def add_item_to_cart():
    """
    Adds a specific product variant to the user's active cart.
    This logic now operates on `variant_id` instead of `product_id`.
    """
    data = request.get_json()
    variant_id = data.get('variant_id')
    quantity = data.get('quantity')
    user_id = get_jwt_identity() # Updated to use the identity from the JWT

    if not all([variant_id, quantity]):
        return jsonify({'error': 'variant_id and quantity are required.'}), 400

    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({'error': 'Quantity must be a positive integer.'}), 400

    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.begin()

        # 1. Lock the specific product variant row to prevent race conditions during check.
        cursor.execute(
            "SELECT inventory_count FROM product_variants WHERE id = %s FOR UPDATE",
            (variant_id,)
        )
        variant = cursor.fetchone()

        if not variant:
            conn.rollback()
            return jsonify({'error': 'Product variant not found.'}), 404

        # 2. Check if there is sufficient stock.
        if variant['inventory_count'] < quantity:
            conn.rollback()
            return jsonify({
                'error': 'Insufficient stock.',
                'available': variant['inventory_count']
            }), 409 # 409 Conflict is a good status code for this

        # 3. Find the user's active cart. Create one if it doesn't exist.
        cursor.execute("SELECT id FROM carts WHERE user_id = %s AND deleted_at IS NULL", (user_id,))
        cart = cursor.fetchone()
        if not cart:
            cursor.execute("INSERT INTO carts (user_id) VALUES (%s)", (user_id,))
            cart_id = cursor.lastrowid
        else:
            cart_id = cart['id']
        
        # 4. Add or update the item in the cart.
        # This uses INSERT ... ON DUPLICATE KEY UPDATE to handle both cases cleanly.
        cursor.execute(
            """
            INSERT INTO cart_items (cart_id, product_variant_id, quantity)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)
            """,
            (cart_id, variant_id, quantity)
        )
        
        conn.commit()
        
        # In a real app, you would return the updated cart state.
        return jsonify({'message': 'Item added to cart successfully.'}), 200

    except Exception as e:
        conn.rollback()
        logger.error(f"Error adding item to cart for user {user_id}: {e}")
        return jsonify({'error': 'An internal error occurred.'}), 500
    finally:
        cursor.close()
        conn.close()

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
