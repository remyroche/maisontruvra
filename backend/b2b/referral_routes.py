from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.referral_service import ReferralService # Assumed service
from backend.auth.permissions import b2b_user_required

b2b_referral_bp = Blueprint('b2b_referral_bp', __name__, url_prefix='/api/b2b/referrals')

# GET the B2B user's referral information
@b2b_referral_bp.route('/', methods=['GET'])
@b2b_user_required
def get_referral_info():
    """
    Get referral information for the currently authenticated B2B user,
    including their unique referral code and a list of referred users.
    """
    user_id = get_jwt_identity()
    try:
        referral_info = ReferralService.get_user_referral_info(user_id)
        if referral_info is None:
            return jsonify(status="error", message="Could not retrieve referral information."), 404

        return jsonify(status="success", data=referral_info), 200
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred while fetching referral information."), 500


        return jsonify({"error": str(e)}), 500
