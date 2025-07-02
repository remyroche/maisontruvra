from flask import current_app, Blueprint, request, jsonify, g
from flask_login import current_user, login_required
from marshmallow import ValidationError
from backend.models import db, Cart, CartItem, Product, User
from backend.services.exceptions import NotFoundException, ServiceError, ValidationException, AuthorizationException
from backend.services.b2b_service import B2BService
from backend.services.inventory_service import InventoryService
from backend.services.monitoring_service import MonitoringService
from backend.services.cart_service import CartService
from backend.utils.input_sanitizer import InputSanitizer
from backend.models.enums import UserType
from backend.schemas import AddToCartSchema, UpdateCartItemSchema
from backend.utils.decorators import api_resource_handler
from decimal import Decimal

cart_bp = Blueprint('cart_bp', __name__, url_prefix='/api/cart')

@cart_bp.route('/', methods=['GET'])
@login_required
def get_cart_contents():
    """
    Gets the contents of the user's cart, with B2B pricing applied if applicable.
    """
    try:
        cart_data = CartService.get_cart(current_user.id)
        if not cart_data or not cart_data.get('items_details'):
            return jsonify({'message': 'Cart is empty', 'items': [], 'total': '0.00', 'subtotal': '0.00', 'discount_applied': '0.00', 'tier_name': None}), 200

        return jsonify({
            'items': [{
                'item_id': detail['item'].id,
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
    """Adds an item to the cart."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'Invalid JSON data provided'}), 400
    
    # Validate input using marshmallow schema
    try:
        schema = AddToCartSchema()
        validated_data = schema.load(json_data)
    except ValidationError as err:
        return jsonify({'message': 'Validation failed', 'errors': err.messages}), 400
        
    try:
        CartService.add_to_cart(current_user.id, validated_data['product_id'], validated_data['quantity'])
        return jsonify({'message': 'Item added to cart'}), 201
    except NotFoundException:
        return jsonify({'message': 'Product not found'}), 404
    except (ValueError, ServiceError) as e:
        return jsonify({'message': str(e)}), 400

@cart_bp.route('/item/<int:item_id>', methods=['PUT'])
@api_resource_handler(
    model=CartItem,
    request_schema=UpdateCartItemSchema,
    response_schema=UpdateCartItemSchema,
    ownership_exempt_roles=[],  # Only the cart owner can update
    cache_timeout=0,  # No caching for cart operations
    log_action=True,
    eager_loads=['cart']  # Need to load cart to check ownership
)
@login_required
def update_cart_item_route(item_id):
    """Updates quantity of a specific item in the cart."""
    # CartItem is already fetched and validated by decorator
    cart_item = g.target_object
    
    # Custom ownership check through cart
    if cart_item.cart.user_id != current_user.id:
        raise AuthorizationException("You do not have permission to update this cart item.")
    
    # Update cart item with validated data
    for key, value in g.validated_data.items():
        if hasattr(cart_item, key):
            setattr(cart_item, key, value)
    
    return cart_item

@cart_bp.route('/item/<int:item_id>', methods=['DELETE'])
@api_resource_handler(
    model=CartItem,
    ownership_exempt_roles=[],  # Only the cart owner can delete
    cache_timeout=0,  # No caching for cart operations
    log_action=True,
    eager_loads=['cart']  # Need to load cart to check ownership
)
@login_required
def remove_cart_item_route(item_id):
    """Removes a specific item from the cart."""
    # CartItem is already fetched and validated by decorator
    cart_item = g.target_object
    
    # Custom ownership check through cart
    if cart_item.cart.user_id != current_user.id:
        raise AuthorizationException("You do not have permission to delete this cart item.")
    
    db.session.delete(cart_item)
    return None  # Decorator will handle the delete response
