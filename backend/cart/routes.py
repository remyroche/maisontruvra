from flask import current_app
from flask_login import current_user
from backend.models import db, Cart, CartItem, Product, User
from backend.services.exceptions import NotFoundException, ServiceError, ValidationException
from backend.services.b2b_service import B2BService
from backend.services.inventory_service import InventoryService
from backend.services.monitoring_service import MonitoringService
from backend.utils.input_sanitizer import InputSanitizer
from backend.models.enums import UserType
from decimal import Decimal

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
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not product_id:
        return jsonify({'message': 'Product ID is required'}), 400
        
    try:
        CartService.add_to_cart(current_user.id, product_id, quantity)
        return jsonify({'message': 'Item added to cart'}), 201
    except NotFoundException:
        return jsonify({'message': 'Product not found'}), 404
    except (ValueError, ServiceError) as e:
        return jsonify({'message': str(e)}), 400

@cart_bp.route('/item/<int:item_id>', methods=['PUT'])
@login_required
def update_cart_item_route(item_id):
    """Updates quantity of a specific item in the cart."""
    data = request.get_json()
    if not data or 'quantity' not in data:
        return jsonify({'message': 'Request body with quantity is missing'}), 400

    try:
        CartService.update_cart_item(current_user.id, item_id, data)
        return jsonify({'message': 'Cart item updated successfully'}), 200
    except NotFoundException as e:
        return jsonify({'message': str(e)}), 404
    except ValidationException as e:
        return jsonify({'message': str(e)}), 400
    except ServiceError as e:
        return jsonify({'message': str(e)}), 400
    except Exception:
        return jsonify({'message': "An internal error occurred"}), 500

@cart_bp.route('/item/<int:item_id>', methods=['DELETE'])
@login_required
def remove_cart_item_route(item_id):
    """Removes a specific item from the cart."""
    try:
        CartService.remove_from_cart(current_user.id, item_id)
        return jsonify({'message': 'Item removed from cart'}), 200
    except NotFoundException as e:
        return jsonify({'message': str(e)}), 404
    except ServiceError as e:
        return jsonify({'message': str(e)}), 400
