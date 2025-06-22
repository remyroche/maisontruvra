
from flask import Blueprint, request, jsonify, session
from backend.models.cart_models import Cart, CartItem
from backend.models.product_models import Product
from backend.models.user_models import User
from backend.database import db
from backend.auth.permissions import auth_required
from flask_jwt_extended import get_jwt_identity, jwt_required
from backend.services.exceptions import NotFoundException, ServiceException

cart_bp = Blueprint('cart_bp', __name__)

@cart_bp.route('/cart', methods=['GET'])
def get_cart():
    """Get cart contents"""
    user_id = None
    try:
        user_id = get_jwt_identity()
    except:
        pass  # Anonymous user
    
    if user_id:
        cart = Cart.query.filter_by(user_id=user_id).first()
    else:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({"items": [], "total": 0}), 200
        cart = Cart.query.filter_by(session_id=session_id).first()
    
    if not cart:
        return jsonify({"items": [], "total": 0}), 200
    
    cart_data = {
        "items": [item.to_dict() for item in cart.items],
        "total": sum(float(item.quantity * item.product.price) for item in cart.items)
    }
    
    return jsonify(cart_data), 200

@cart_bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    """Add item to cart"""
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    user_id = None
    try:
        user_id = get_jwt_identity()
    except:
        pass
    
    # Get or create cart
    if user_id:
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            db.session.add(cart)
    else:
        session_id = session.get('session_id')
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
        
        cart = Cart.query.filter_by(session_id=session_id).first()
        if not cart:
            cart = Cart(session_id=session_id)
            db.session.add(cart)
    
    # Check if item already in cart
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    
    try:
        db.session.commit()
        return jsonify({"message": "Item added to cart"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@cart_bp.route('/cart/update', methods=['PUT'])
def update_cart_item():
    """Update cart item quantity"""
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    
    user_id = None
    try:
        user_id = get_jwt_identity()
    except:
        pass
    
    if user_id:
        cart = Cart.query.filter_by(user_id=user_id).first()
    else:
        session_id = session.get('session_id')
        cart = Cart.query.filter_by(session_id=session_id).first()
    
    if not cart:
        return jsonify({"error": "Cart not found"}), 404
    
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if not cart_item:
        return jsonify({"error": "Item not in cart"}), 404
    
    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity
    
    try:
        db.session.commit()
        return jsonify({"message": "Cart updated"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@cart_bp.route('/cart/remove/<int:product_id>', methods=['DELETE'])
def remove_from_cart(product_id):
    """Remove item from cart"""
    user_id = None
    try:
        user_id = get_jwt_identity()
    except:
        pass
    
    if user_id:
        cart = Cart.query.filter_by(user_id=user_id).first()
    else:
        session_id = session.get('session_id')
        cart = Cart.query.filter_by(session_id=session_id).first()
    
    if not cart:
        return jsonify({"error": "Cart not found"}), 404
    
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
    
    return jsonify({"message": "Item removed from cart"}), 200

