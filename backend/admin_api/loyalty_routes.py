from flask import Blueprint, jsonify, request
from backend.services.b2b_loyalty_service import B2BLoyaltyService
from backend.services.exceptions import ServiceException, NotFoundException
from backend.auth.permissions import admin_required

loyalty_routes = Blueprint('admin_loyalty_routes', __name__)

@loyalty_routes.route('/loyalty/tiers', methods=['GET'])
@admin_required
def get_loyalty_tiers():
    try:
        tiers = B2BLoyaltyService.get_all_tiers()
        return jsonify([tier.to_dict() for tier in tiers]), 200
    except ServiceException as e:
        return jsonify({"error": str(e)}), 500

@loyalty_routes.route('/loyalty/tiers', methods=['POST'])
@admin_required
def create_loyalty_tier():
    data = request.get_json()
    try:
        tier = B2BLoyaltyService.create_tier(data)
        return jsonify(tier.to_dict()), 201
    except ServiceException as e:
        return jsonify({"error": str(e)}), 400

@loyalty_routes.route('/loyalty/tiers/<int:tier_id>', methods=['PUT'])
@admin_required
def update_loyalty_tier(tier_id):
    data = request.get_json()
    try:
        tier = B2BLoyaltyService.update_tier(tier_id, data)
        return jsonify(tier.to_dict()), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except ServiceException as e:
        return jsonify({"error": str(e)}), 400

@loyalty_routes.route('/loyalty/tiers/<int:tier_id>', methods=['DELETE'])
@admin_required
def delete_loyalty_tier(tier_id):
    try:
        B2BLoyaltyService.delete_tier(tier_id)
        return jsonify({"message": "Tier deleted successfully"}), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except ServiceException as e:
        return jsonify({"error": str(e)}), 500

@loyalty_routes.route('/loyalty/assign-tiers', methods=['POST'])
@admin_required
def assign_tiers_manually():
    """Endpoint to manually trigger the tier assignment task."""
    from backend.tasks import update_b2b_loyalty_tiers_task
    task = update_b2b_loyalty_tiers_task.delay()
    return jsonify({"message": "Tier assignment task has been triggered.", "task_id": task.id}), 202
