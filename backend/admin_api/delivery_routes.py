from flask import Blueprint, request, jsonify
from backend.auth.permissions import permissions_required
from backend.services.delivery_service import DeliveryService
from backend.services.loyalty_service import LoyaltyService

delivery_admin_bp = Blueprint('delivery_admin_bp', __name__, url_prefix='/admin/delivery-methods')

@delivery_admin_bp.route('/', methods=['GET'])
@permissions_required('MANAGE_DELIVERY')
def get_delivery_methods():
    """Admin endpoint to get all delivery methods."""
    methods = DeliveryService.get_all_methods_for_admin()
    return jsonify(status="success", data=methods)

@delivery_admin_bp.route('/tiers', methods=['GET'])
@permissions_required('MANAGE_DELIVERY')
def get_all_tiers():
    """Helper endpoint to get all loyalty tiers for the form."""
    tiers = LoyaltyService.get_all_tier_discounts() # Reusing this as it returns names and discounts
    return jsonify(status="success", data=tiers)

@delivery_admin_bp.route('/', methods=['POST'])
@permissions_required('MANAGE_DELIVERY')
def create_delivery_method():
    """Admin endpoint to create a new delivery method."""
    data = request.get_json()
    if not data or not data.get('name') or 'price' not in data:
        return jsonify(status="error", message="Name and price are required."), 400
    
    try:
        new_method = DeliveryService.create_method(data)
        return jsonify(status="success", data=new_method.to_dict()), 201
    except Exception as e:
        return jsonify(status="error", message=str(e)), 500


@delivery_admin_bp.route('/<int:method_id>', methods=['PUT'])
@permissions_required('MANAGE_DELIVERY')
def update_delivery_method(method_id):
    """Admin endpoint to update a delivery method."""
    data = request.get_json()
    try:
        updated_method = DeliveryService.update_method(method_id, data)
        return jsonify(status="success", data=updated_method.to_dict())
    except Exception as e:
        return jsonify(status="error", message=str(e)), 500

@delivery_admin_bp.route('/<int:method_id>', methods=['DELETE'])
@permissions_required('MANAGE_DELIVERY')
def delete_delivery_method(method_id):
    """Admin endpoint to delete a delivery method."""
    try:
        if DeliveryService.delete_method(method_id):
            return jsonify(status="success", message="Delivery method deleted successfully."), 200
        else:
            return jsonify(status="error", message="Method not found."), 404
    except Exception as e:
        return jsonify(status="error", message=str(e)), 500


# --- Public-Facing API ---
delivery_public_bp = Blueprint('delivery_public_bp', __name__, url_prefix='/api/delivery-methods')

@delivery_public_bp.route('/', methods=['GET'])
@jwt_required()
def get_public_delivery_methods():
    """Public endpoint for B2B users to fetch available delivery methods."""
    user_id = get_jwt_identity()
    try:
        methods = DeliveryService.get_available_methods_for_user(user_id)
        return jsonify(status="success", data=methods)
    except Exception as e:
        return jsonify(status="error", message=str(e)), 500
