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

@loyalty_bp.route('/points-breakdown', methods=['GET'])
@b2b_login_required
def get_points_breakdown():
    """
    New endpoint to provide a detailed breakdown of loyalty points.
    """
    b2b_user_id = session.get('b2b_user_id')
    loyalty_service = LoyaltyService(db.session)
    
    try:
        breakdown = loyalty_service.get_points_breakdown(b2b_user_id)
        return jsonify(breakdown)
    except Exception as e:
        # In a real app, log the error e
        return jsonify({"error": "Could not retrieve loyalty points breakdown."}), 500

@b2b_loyalty_bp.route('/program-details', methods=['GET'])
@b2b_user_required
@cache.cached(timeout=21600)
def get_loyalty_program_details():
    """
    Get all necessary information for the loyalty page.
    This is now optimized to only fetch dynamic data:
    1. The current user's status (points, tier, referral code).
    2. A list of all available tiers with their admin-defined discount percentages.
    """
    user_id = get_jwt_identity()
    try:
        user_status = LoyaltyService.get_user_loyalty_status(user_id)
        
        # This method in LoyaltyService should be created to return a simple list:
        # e.g., [{'name': 'Partenaire', 'discount_percentage': 10}, ...]
        tier_discounts = LoyaltyService.get_all_tier_discounts() 
        
        if user_status is None:
            return jsonify(status="error", message="Could not retrieve loyalty information for this user."), 404
            
        return jsonify(status="success", data={
            "userStatus": user_status,
            "tierDiscounts": tier_discounts
        }), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal error occurred while fetching loyalty program details."), 500
