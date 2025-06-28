from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.checkout_service import CheckoutService
from backend.utils.sanitization import sanitize_input
from backend.services.exceptions import NotFoundException, ValidationException

checkout_bp = Blueprint('checkout_bp', __name__, url_prefix='/api')

@checkout_bp.route('/user/addresses', methods=['GET'])
@jwt_required()
def get_user_addresses():
    """Fetches all addresses for the currently authenticated user."""
    user_id = get_jwt_identity()
    try {
        addresses = CheckoutService.get_user_addresses(user_id)
        return jsonify(addresses=[address.to_dict() for address in addresses])
    } catch (NotFoundException as e) {
        return jsonify(error=str(e)), 404
    }

@checkout_bp.route('/user/addresses', methods=['POST'])
@jwt_required()
def add_user_address():
    """Adds a new address for the currently authenticated user."""
    user_id = get_jwt_identity()
    data = sanitize_input(request.get_json())
    try {
        address = CheckoutService.add_user_address(user_id, data)
        return jsonify(address=address.to_dict()), 201
    } catch (ValidationException as e) {
        return jsonify(error=str(e)), 400
    }

@checkout_bp.route('/user/addresses/<int:address_id>', methods=['PUT'])
@jwt_required()
def update_user_address(address_id):
    """Updates an existing address for the currently authenticated user."""
    user_id = get_jwt_identity()
    data = sanitize_input(request.get_json())
    try {
        address = CheckoutService.update_user_address(user_id, address_id, data)
        return jsonify(address=address.to_dict())
    } catch (NotFoundException as e) {
        return jsonify(error=str(e)), 404
    }

@checkout_bp.route('/delivery/methods', methods=['GET'])
def get_delivery_methods():
    """Gets available delivery methods based on address and cart total."""
    # In a real app, you'd pass address and cart data from request.args
    # For now, we fetch all available methods.
    methods = CheckoutService.get_available_delivery_methods(address={}, cart_total=0)
    return jsonify(delivery_methods=[method.to_dict() for method in methods])