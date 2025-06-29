from flask import Blueprint, request, jsonify
from ..services.loyalty_service import LoyaltyService
from ..utils.sanitization import sanitize_input
from backend.utils.decorators import staff_required, roles_required, permissions_required
from ..extensions import cache

loyalty_bp = Blueprint('admin_loyalty_routes', __name__, url_prefix='/api/admin/loyalty')

# --- Loyalty Program Tier Management ---

@loyalty_bp.route('/tiers', methods=['GET'])
@roles_required('ADMIN', 'MANAGER')
@permissions_required('MANAGE_LOYALTY_PROGRAM')
def get_tiers():
    """Gets all loyalty tiers."""
    tiers = LoyaltyService.get_all_tiers()
    return jsonify([tier.to_dict() for tier in tiers])

@loyalty_bp.route('/tiers', methods=['POST'])
@roles_required('ADMIN', 'MANAGER')
@permissions_required('MANAGE_LOYALTY_PROGRAM')
def create_tier():
    """Creates a new loyalty tier."""
    data = request.get_json()
    try:
        tier = LoyaltyService.create_tier(
            name=data['name'],
            min_spend=data['min_spend'],
            points_per_euro=data.get('points_per_euro', 1.0),
            benefits=data.get('benefits', '')
        )
        cache.delete('view//b2b/loyalty/program-details')
        return jsonify(tier.to_dict()), 201
    except Exception as e:
        # In a real app, you'd log the error `e`
        return jsonify({"error": "Failed to create tier.", "details": str(e)}), 400

@loyalty_bp.route('/tiers/<uuid:tier_id>', methods=['PUT'])
@roles_required('ADMIN', 'MANAGER')
@permissions_required('MANAGE_LOYALTY_PROGRAM')
def update_tier(tier_id):
    """Updates an existing loyalty tier."""
    data = request.get_json()
    tier = LoyaltyService.update_loyalty_tier(tier_id, data)
    cache.delete('view//b2b/loyalty/program-details')
    if not tier:
        return jsonify({"error": "Tier not found"}), 404
    return jsonify(tier.to_dict())

@loyalty_bp.route('/tiers/<uuid:tier_id>', methods=['DELETE'])
@roles_required('ADMIN', 'MANAGER')
@permissions_required('MANAGE_LOYALTY_PROGRAM')
def delete_tier(tier_id):
    """Deletes a loyalty tier."""
    if LoyaltyService.delete_tier(tier_id):
        cache.delete('view//b2b/loyalty/program-details')
        return jsonify({"message": "Tier deleted successfully"})
    return jsonify({"error": "Tier not found"}), 404

# --- Referral Reward Tier Management ---

@loyalty_bp.route('/referral-rewards', methods=['GET'])
@roles_required('ADMIN', 'MANAGER')
@permissions_required('MANAGE_LOYALTY_PROGRAM')
def get_referral_rewards():
    """Gets all referral reward tiers."""
    rewards = LoyaltyService.get_referral_reward_tiers()
    return jsonify([{'id': str(r.id), 'referral_count': r.referral_count, 'reward_description': r.reward_description} for r in rewards])

@loyalty_bp.route('/referral-rewards', methods=['POST'])
@roles_required('ADMIN', 'MANAGER')
@permissions_required('MANAGE_LOYALTY_PROGRAM')
def create_referral_reward():
    """Creates a new referral reward tier."""
    data = request.get_json()
    reward = LoyaltyService.create_referral_reward_tier(data)
    return jsonify({'id': str(reward.id)}), 201


# --- General Loyalty Settings ---

@loyalty_bp.route('/settings', methods=['GET'])
@roles_required('ADMIN', 'MANAGER')
@permissions_required('MANAGE_LOYALTY_PROGRAM')
def get_loyalty_settings():
    """Gets the current settings for the loyalty program."""
    try:
        settings = LoyaltyService.get_settings()
        return jsonify(status="success", data=settings), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="Failed to retrieve loyalty settings."), 500

@loyalty_bp.route('/settings', methods=['PUT'])
@roles_required('ADMIN', 'MANAGER')
@permissions_required('MANAGE_LOYALTY_PROGRAM')
def update_loyalty_settings():
    """Updates the settings for the loyalty program."""
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Invalid JSON body"), 400

    sanitized_data = sanitize_input(data)

    try:
        updated_settings = LoyaltyService.update_settings(sanitized_data)
        return jsonify(status="success", data=updated_settings), 200
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="Failed to update loyalty settings."), 500

# --- Manual Point Adjustments ---

@loyalty_bp.route('/users/<uuid:user_id>/points', methods=['POST'])
@roles_required('ADMIN', 'MANAGER')
@permissions_required('MANAGE_LOYALTY_PROGRAM')
def adjust_user_points(user_id):
    """Manually adds or removes loyalty points for a specific user."""
    data = request.get_json()
    if not data or 'points' not in data or 'reason' not in data:
        return jsonify(status="error", message="'points' (integer) and 'reason' (string) are required."), 400

    try:
        points = int(sanitize_input(data['points']))
        reason = sanitize_input(data['reason'])

        updated_balance = LoyaltyService.adjust_points(user_id, points, reason)
        return jsonify(status="success", data={'new_balance': updated_balance}), 200
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 404
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="Failed to adjust user points."), 500

