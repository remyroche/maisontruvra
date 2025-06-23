from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.b2b_service import B2BService
from backend.utils.sanitization import sanitize_input
from backend.auth.permissions import b2b_user_required

b2b_profile_bp = Blueprint('b2b_profile_bp', __name__, url_prefix='/api/b2b/profile')

# GET the B2B user's company profile
@b2b_profile_bp.route('/', methods=['GET'])
@b2b_user_required
def get_b2b_profile():
    """
    Get the company profile associated with the currently authenticated B2B user.
    """
    user_id = get_jwt_identity()
    try:
        # Assumes the service can find the company profile linked to the user
        profile = B2BService.get_company_profile_by_user(user_id)
        if not profile:
            return jsonify(status="error", message="B2B profile not found for this user."), 404
        
        return jsonify(status="success", data=profile.to_dict()), 200
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An error occurred while fetching the B2B profile."), 500

# UPDATE the B2B user's company profile
@b2b_profile_bp.route('/', methods=['PUT'])
@b2b_user_required
def update_b2b_profile():
    """
    Update the company profile information for the authenticated B2B user.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Invalid or missing JSON body"), 400

    sanitized_data = sanitize_input(data)
    
    # Remove sensitive fields that should not be changed here
    sanitized_data.pop('vat_number', None)
    sanitized_data.pop('status', None) # Status should only be changed by an admin

    try:
        updated_profile = B2BService.update_company_profile_by_user(user_id, sanitized_data)
        if not updated_profile:
            return jsonify(status="error", message="B2B Profile not found or update failed"), 404
        return jsonify(status="success", data=updated_profile.to_dict()), 200
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred while updating the B2B profile."), 500


@b2b_profile_bp.route('/address', methods=['POST'])
@b2b_required
def add_b2b_address():
    data = sanitize_input(request.get_json())
    address = b2b_user_service.add_address(current_user.id, data)
    return jsonify(address.to_dict()), 201

@b2b_profile_bp.route('/address/<int:address_id>', methods=['PUT'])
@b2b_required
def update_b2b_address(address_id):
    data = sanitize_input(request.get_json())
    address = b2b_user_service.update_address(address_id, data, current_user.id)
    return jsonify(address.to_dict())

@b2b_profile_bp.route('/address/<int:address_id>', methods=['DELETE'])
@b2b_required
def delete_b2b_address(address_id):
    b2b_user_service.delete_address(address_id, current_user.id)
    return jsonify({'message': 'Address deleted'})

