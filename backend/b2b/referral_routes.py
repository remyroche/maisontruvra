
from flask import Blueprint, request, jsonify
from backend.auth.permissions import b2b_user_required
from flask_jwt_extended import get_jwt_identity
from backend.services.b2b_referral_service import B2BReferralService
from backend.services.exceptions import ServiceException

referral_routes = Blueprint('b2b_referral_routes', __name__)

@referral_routes.route('/referrals', methods=['POST'])
@b2b_user_required
def create_referral():
    """
    A B2B user refers another potential business.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        referral = B2BReferralService.create_referral(user_id, data)
        return jsonify(referral.to_dict()), 201
    except ServiceException as e:
        return jsonify({"error": str(e)}), 400

@referral_routes.route('/referrals', methods=['GET'])
@b2b_user_required
def get_my_referrals():
    """
    Get the status of all referrals made by the logged-in B2B user.
    """
    user_id = get_jwt_identity()
    try:
        referrals = B2BReferralService.get_referrals_by_user(user_id)
        return jsonify([r.to_dict() for r in referrals]), 200
    except ServiceException as e:
        return jsonify({"error": str(e)}), 500