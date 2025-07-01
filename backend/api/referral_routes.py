from flask import Blueprint, jsonify, current_app
from backend.services.referral_service import ReferralService
from backend.utils.decorators import login_required
from flask_login import current_user

referral_bp = Blueprint('referral_api', __name__, url_prefix='/api/referrals')

@referral_bp.route('/my-code', methods=['GET'])
@login_required
def get_my_referral_code():
    """
    Generates and/or retrieves the current user's referral code.
    """
    logger = current_app.logger
    referral_service = ReferralService(logger)
    try:
        code = referral_service.generate_referral_code(current_user.id)
        return jsonify({"referral_code": code}), 200
    except Exception as e:
        logger.exception(f"Error getting referral code for user {current_user.id}.")
        return jsonify({"error": "An internal error occurred."}), 500

@referral_bp.route('/my-status', methods=['GET'])
@login_required
def get_my_referral_status():
    """
    Retrieves the user's referral status, including their tier and number of completed referrals.
    """
    # This logic would live in the ReferralService, which would query the Referral model.
    # For brevity, a placeholder is shown here.
    return jsonify({
        "tier": current_user.referral_tier.name if current_user.referral_tier else "Standard",
        "completed_referrals": len([r for r in current_user.referrals_made if r.status == 'completed'])
    }), 200
