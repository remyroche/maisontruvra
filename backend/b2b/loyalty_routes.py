from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.loyalty_service import LoyaltyService
from backend.auth.permissions import b2b_user_required

b2b_loyalty_bp = Blueprint('b2b_loyalty_bp', __name__, url_prefix='/api/b2b/loyalty')

# GET the B2B user's loyalty points and tier information
@b2b_loyalty_bp.route('/status', methods=['GET'])
@b2b_user_required
def get_loyalty_status():
    """
    Get the loyalty status, including points balance and current tier,
    for the authenticated B2B user.
    """
    user_id = get_jwt_identity()
    try:
        loyalty_info = LoyaltyService.get_user_loyalty_status(user_id)
        if loyalty_info is None:
            return jsonify(status="error", message="Could not retrieve loyalty information for this user."), 404
        
        return jsonify(status="success", data=loyalty_info), 200
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred while fetching loyalty status."), 500

