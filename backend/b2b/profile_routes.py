from flask import Blueprint, request, jsonify
from backend.auth.permissions import b2b_user_required
from flask_jwt_extended import get_jwt_identity
from backend.services.b2b_partnership_service import B2BPartnershipService
from backend.services.exceptions import ServiceException, NotFoundException

profile_routes = Blueprint('b2b_profile_routes', __name__)

@profile_routes.route('/profile', methods=['GET'])
@b2b_user_required
def get_b2b_profile():
    """
    Get the B2B company profile for the logged-in user.
    """
    user_id = get_jwt_identity()
    try:
        b2b_profile = B2BPartnershipService.get_b2b_profile_by_user_id(user_id)
        return jsonify(b2b_profile.to_dict()), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404

@profile_routes.route('/profile', methods=['PUT'])
@b2b_user_required
def update_b2b_profile():
    """
    Update the B2B company profile.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        b2b_profile = B2BPartnershipService.get_b2b_profile_by_user_id(user_id)
        updated_profile = B2BPartnershipService.update_b2b_user(b2b_profile.id, data)
        return jsonify(updated_profile.to_dict()), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except ServiceException as e:
        return jsonify({"error": str(e)}), 400