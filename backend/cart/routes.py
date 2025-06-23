from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from backend.services.cart_service import CartService
from backend.utils.sanitization import sanitize_input

cart_bp = Blueprint('cart_bp', __name__, url_prefix='/api/cart')

def get_session_id():
    """
    Placeholder for getting a unique session ID for anonymous users.
    In a real app, this would likely come from a session cookie.
    """
    # For demonstration, we'll use a header, but a session cookie is better.
    return request.headers.get('X-Session-ID')

@cart_bp.route('/', methods=['GET'])
@jwt_required(optional=True)
def get_cart_contents():
    """
    Get the contents of the user's cart.
    Works for both authenticated users (via JWT) and anonymous users (via session).
    """
    user_id = get_jwt_identity()
    try:
        if user_id:
            cart = CartService.get_cart_by_user_id(user_id)
        else:
            session_id = get_session_id()
            if not session_id:
                return jsonify(status="success", data={"items": [], "total": 0}), 200 # Return empty cart
            cart = CartService.get_cart_by_session_id(session_id)
        
        return jsonify(status="success", data=cart.to_dict() if cart else {"items": [], "total": 0}), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An error occurred while fetching the cart."), 500

@cart_bp.route('/item', methods=['POST'])
@jwt_required(optional=True)
def add_item_to_cart():
    """
    Add an item to the cart.
    """
    user_id = get_jwt_identity()
    session_id = get_session_id() if not user_id else None
    if not user_id and not session_id:
        return jsonify(status="error", message="Authentication or session ID is required."), 401

    data = request.get_json()
    if not data or 'product_id' not in data or 'quantity' not in data:
        return jsonify(status="error", message="product_id and quantity are required."), 400

    try:
        product_id = int(sanitize_input(data['product_id']))
        quantity = int(sanitize_input(data['quantity']))

        if quantity <= 0:
            return jsonify(status="error", message="Quantity must be a positive number."), 400
            
        updated_cart = CartService.add_item(user_id=user_id, session_id=session_id, product_id=product_id, quantity=quantity)
        return jsonify(status="success", data=updated_cart.to_dict()), 200
    except ValueError:
        return jsonify(status="error", message="Invalid product_id or quantity format."), 400
    except Exception as e:
        # Log error e
        return jsonify(status="error", message=str(e)), 500

@cart_bp.route('/item/<int:product_id>', methods=['PUT'])
@jwt_required(optional=True)
def update_cart_item(product_id):
    """
    Update the quantity of an item in the cart.
    """
    user_id = get_jwt_identity()
    session_id = get_session_id() if not user_id else None
    if not user_id and not session_id:
        return jsonify(status="error", message="Authentication or session ID is required."), 401
    
    data = request.get_json()
    if not data or 'quantity' not in data:
        return jsonify(status="error", message="Quantity is required."), 400

    try:
        quantity = int(sanitize_input(data['quantity']))
        if quantity < 0:
             return jsonify(status="error", message="Quantity cannot be negative."), 400

        updated_cart = CartService.update_item_quantity(user_id=user_id, session_id=session_id, product_id=product_id, quantity=quantity)
        return jsonify(status="success", data=updated_cart.to_dict()), 200
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 404 # e.g. "Item not in cart"
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An error occurred while updating the cart."), 500

@cart_bp.route('/item/<int:product_id>', methods=['DELETE'])
@jwt_required(optional=True)
def remove_cart_item(product_id):
    """
    Remove an item from the cart.
    """
    user_id = get_jwt_identity()
    session_id = get_session_id() if not user_id else None
    if not user_id and not session_id:
        return jsonify(status="error", message="Authentication or session ID is required."), 401

    try:
        updated_cart = CartService.remove_item(user_id=user_id, session_id=session_id, product_id=product_id)
        return jsonify(status="success", data=updated_cart.to_dict()), 200
    except ValueError as e:
         return jsonify(status="error", message=str(e)), 404
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An error occurred while removing the item from the cart."), 500

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

