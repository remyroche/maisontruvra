from flask import Blueprint, jsonify
from backend.auth.permissions import b2b_user_required
from flask_jwt_extended import get_jwt_identity
from backend.services.user_service import UserService
from backend.services.b2b_loyalty_service import B2BLoyaltyService
from backend.services.exceptions import ServiceException

loyalty_routes = Blueprint('b2b_loyalty_routes', __name__)

@loyalty_routes.route('/loyalty/status', @b2b_bp.route('/loyalty', methods=['GET'])
@b2b_user_required
def get_loyalty_status():
    """
    Returns the current B2B user's loyalty status, including their
    points, tier, and personal referral code.
    """
    user_id = get_jwt_identity()

    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Fetch user's points, referral code, and tier information in a single query.
        cursor.execute(
            """
            SELECT
                u.points,
                u.referral_code,
                t.name as tier_name,
                t.discount_percentage
            FROM users u
            JOIN b2b_profiles bp ON u.id = bp.user_id
            JOIN b2b_tiers t ON bp.tier_id = t.id
            WHERE u.id = %s
            """,
            (user_id,)
        )
        loyalty_data = cursor.fetchone()

        if not loyalty_data:
            return jsonify({"error": "Could not retrieve loyalty information for this user."}), 404

        return jsonify(loyalty_data), 200

    except Exception as e:
        logger.error(f"Error fetching loyalty status for B2B user {user_id}: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500
    finally:
        cursor.close()
        conn.close()
