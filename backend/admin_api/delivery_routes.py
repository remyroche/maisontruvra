from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.utils.decorators import staff_required, roles_required, permissions_required
from ..utils.input_sanitizer import InputSanitizer
from backend.services.delivery_service import DeliveryService
from backend.services.loyalty_service import LoyaltyService

# This blueprint is registered in __init__.py with the prefix /api/admin/delivery
admin_delivery_bp = Blueprint('admin_delivery_bp', __name__)

@admin_delivery_bp.route('/settings', methods=['GET'])
@permissions_required('MANAGE_DELIVERY')
@roles_required ('Admin', 'Manager')
def get_settings():
    """Get all delivery countries and options."""
    settings = DeliveryService.get_delivery_settings()
    return jsonify(status="success", data=settings), 200

@admin_delivery_bp.route('/settings', methods=['POST'])
@permissions_required('MANAGE_DELIVERY')
@roles_required ('Admin', 'Manager')
def update_settings():
    """Update delivery settings."""
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="No data provided"), 400
    
    DeliveryService.update_delivery_settings(data)
    return jsonify(status="success", message="Delivery settings updated successfully"), 200


@admin_delivery_bp.route('/', methods=['GET'])
@permissions_required('MANAGE_DELIVERY')
@roles_required ('Admin', 'Manager')
def get_delivery_methods():
    """Admin endpoint to get all delivery methods."""
    methods = DeliveryService.get_all_methods_for_admin()
    return jsonify(status="success", data=methods), 200

@admin_delivery_bp.route('/tiers', methods=['GET'])
@permissions_required('MANAGE_DELIVERY')
@roles_required ('Admin', 'Manager')
def get_all_tiers():
    """Helper endpoint to get all loyalty tiers for the form."""
    tiers = LoyaltyService.get_all_tier_discounts() # Reusing this as it returns names and discounts
    return jsonify(status="success", data=tiers), 200

@admin_delivery_bp.route('/', methods=['POST'])
@permissions_required('MANAGE_DELIVERY')
@roles_required ('Admin', 'Manager')
def create_delivery_method():
    """Admin endpoint to create a new delivery method."""
    data = InputSanitizer.recursive_sanitize(request.get_json())
    if not data or not data.get('name') or 'price' not in data:
        return jsonify(status="error", message="Name and price are required."), 400
    
    try:
        new_method = DeliveryService.create_method(data)
        return jsonify(status="success", data=new_method.to_dict()), 201
    except Exception as e:
        return jsonify(status="error", message=str(e)), 500


@admin_delivery_bp.route('/<int:method_id>', methods=['PUT'])
@permissions_required('MANAGE_DELIVERY')
@roles_required ('Admin', 'Manager')
def update_delivery_method(method_id):
    """Admin endpoint to update a delivery method."""
    data = InputSanitizer.recursive_sanitize(request.get_json())
    try:
        updated_method = DeliveryService.update_method(method_id, data)
        return jsonify(status="success", data=updated_method.to_dict()), 200
    except Exception as e:
        return jsonify(status="error", message=str(e)), 500

@admin_delivery_bp.route('/<int:method_id>', methods=['DELETE'])
@permissions_required('MANAGE_DELIVERY')
@roles_required ('Admin', 'Manager')
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
# Note: This blueprint is not currently registered in backend/__init__.py
delivery_public_bp = Blueprint('delivery_public_bp', __name__)

@delivery_public_bp.route('/', methods=['GET'])
@jwt_required() # Assuming this is for authenticated B2C/B2B users
def get_public_delivery_methods():
    """Public endpoint for authenticated users to fetch available delivery methods."""
    user_id = get_jwt_identity()
    try:
        methods = DeliveryService.get_available_methods_for_user(user_id)
        return jsonify(status="success", data=methods), 200
    except Exception as e:
        return jsonify(status="error", message=str(e)), 500
