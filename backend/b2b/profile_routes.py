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

@b2b_profile_bp.route('/profile', methods=['POST', 'PUT'])
@jwt_required()
def update_b2b_profile():
    b2b_user_id = get_jwt_identity()
    profile = B2BUserProfile.query.filter_by(b2b_user_id=b2b_user_id).first()

    data = request.get_json()
    sanitized_data = sanitize_input(data)

    if not profile:
        profile = B2BUserProfile(b2b_user_id=b2b_user_id)
        db.session.add(profile)

    # Update fields from sanitized data
    profile.contact_person = sanitized_data.get('contact_person', profile.contact_person)
    profile.phone_number = sanitized_data.get('phone_number', profile.phone_number)
    profile.address_line1 = sanitized_data.get('address_line1', profile.address_line1)
    profile.address_line2 = sanitized_data.get('address_line2', profile.address_line2)
    profile.city = sanitized_data.get('city', profile.city)
    profile.state = sanitized_data.get('state', profile.state)
    profile.postal_code = sanitized_data.get('postal_code', profile.postal_code)
    profile.country = sanitized_data.get('country', profile.country)
    
    db.session.commit()

    return jsonify({"msg": "B2B profile updated successfully"}), 200
