from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.extensions import cache
from backend.services.loyalty_service import LoyaltyService
from backend.utils.decorators import b2b_user_required

b2b_loyalty_bp = Blueprint("b2b_loyalty_bp", __name__, url_prefix="/api/b2b/loyalty")


@b2b_loyalty_bp.route("/status", methods=["GET"])
@jwt_required()
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
            return jsonify(
                status="error",
                message="Could not retrieve loyalty information for this user.",
            ), 404

        # Assuming get_user_loyalty_status returns an object with a to_dict() method
        return jsonify(status="success", data=loyalty_info.to_dict()), 200
    except Exception:
        # Log the error e
        return jsonify(
            status="error",
            message="An internal error occurred while fetching loyalty status.",
        ), 500


@b2b_loyalty_bp.route("/points-breakdown", methods=["GET"])
@jwt_required()
@b2b_user_required
def get_points_breakdown():
    """
    New endpoint to provide a detailed breakdown of loyalty points.
    """
    user_id = get_jwt_identity()
    try:
        breakdown = LoyaltyService.get_points_breakdown(user_id)
        return jsonify(breakdown)
    except Exception:
        # In a real app, log the error e
        return jsonify({"error": "Could not retrieve loyalty points breakdown."}), 500


@b2b_loyalty_bp.route("/program-details", methods=["GET"])
@jwt_required()
@b2b_user_required
@cache.cached(timeout=3600)  # Cache for 1 hour
def get_loyalty_program_details():
    """
    Get all necessary information for the loyalty page.
    """
    user_id = get_jwt_identity()
    try:
        user_status = LoyaltyService.get_user_loyalty_status(user_id)
        tier_details = LoyaltyService.get_all_tiers()

        if user_status is None:
            # Create a default loyalty status for new users if they don't have one
            user_status = LoyaltyService.create_initial_loyalty_status(user_id)

        return jsonify(
            status="success",
            data={
                "userStatus": user_status.to_dict() if user_status else None,
                "tiers": [tier.to_dict() for tier in tier_details],
            },
        ), 200
    except Exception:
        # Log error e
        return jsonify(
            status="error",
            message="An internal error occurred while fetching loyalty program details.",
        ), 500


@b2b_loyalty_bp.route("/referral-code", methods=["GET"])
@jwt_required()
@b2b_user_required
def get_referral_code():
    """Generates or retrieves a referral code for the user."""
    user_id = get_jwt_identity()
    referral = LoyaltyService.get_referral_data(user_id)
    if not referral:
        referral = LoyaltyService.create_referral_code(user_id)

    if referral:
        return jsonify({"referral_code": referral.referral_code})
    return jsonify({"message": "Could not generate referral code"}), 500


@b2b_loyalty_bp.route("/referrals", methods=["GET"])
@jwt_required()
@b2b_user_required
def get_user_referrals():
    """Gets a list of users referred by the current user."""
    user_id = get_jwt_identity()
    referrals = LoyaltyService.get_referrals_for_user(user_id)
    return jsonify(
        [
            {
                "referred_user_email": r.referred.email if r.referred else "N/A",
                "status": r.status,
            }
            for r in referrals
        ]
    )


@b2b_loyalty_bp.route("/convert-points", methods=["POST"])
@jwt_required()
@b2b_user_required
def convert_points():
    """Converts loyalty points into a voucher."""
    user_id = get_jwt_identity()
    data = request.get_json()
    points = data.get("points")
    amount = data.get("amount")
    voucher = LoyaltyService.convert_points_to_voucher(user_id, points, amount)
    if voucher:
        return jsonify(
            {
                "voucher_code": voucher.voucher_code,
                "discount_amount": voucher.discount_amount,
            }
        )
    return jsonify(
        {"message": "Conversion failed. Not enough points or invalid amount."}
    ), 400


@b2b_loyalty_bp.route("/exclusive-rewards", methods=["GET"])
@jwt_required()
@b2b_user_required
def get_rewards():
    """Gets the exclusive rewards available to the user's tier."""
    user_id = get_jwt_identity()
    loyalty_status = LoyaltyService.get_user_loyalty_status(user_id)
    tier_id = loyalty_status.tier_id if loyalty_status else None
    rewards = LoyaltyService.get_exclusive_rewards(tier_id)
    return jsonify([r.to_dict() for r in rewards])


@b2b_loyalty_bp.route("/redeem-reward", methods=["POST"])
@jwt_required()
@b2b_user_required
def redeem_reward():
    """Redeems an exclusive reward using loyalty points."""
    user_id = get_jwt_identity()
    data = request.get_json()
    reward_id = data.get("reward_id")
    success = LoyaltyService.redeem_exclusive_reward(user_id, reward_id)
    if success:
        return jsonify({"message": "Reward redeemed successfully"})
    return jsonify(
        {"message": "Redemption failed. Not enough points or reward not available."}
    ), 400
