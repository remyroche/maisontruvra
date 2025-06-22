from flask import Blueprint, jsonify
from backend.auth.permissions import b2b_user_required
from flask_jwt_extended import get_jwt_identity
from backend.services.user_service import UserService
from backend.services.b2b_loyalty_service import B2BLoyaltyService
from backend.services.exceptions import ServiceException

loyalty_routes = Blueprint('b2b_loyalty_routes', __name__)

@loyalty_routes.route('/loyalty/status', methods=['GET'])
@b2b_user_required
def get_loyalty_status():
    """
    Get the loyalty program status for the logged-in B2B user.
    """
    user_id = get_jwt_identity()
    b2b_user = UserService.get_b2b_profile_by_user_id(user_id)
    
    if not b2b_user:
        return jsonify({"error": "B2B profile not found"}), 404
        
    try:
        status = B2BLoyaltyService.get_user_loyalty_status(b2b_user.id)
        return jsonify(status), 200
    except ServiceException as e:
        return jsonify({"error": str(e)}), 500
