from flask import Blueprint, request, jsonify
from backend.services.loyalty_service import LoyaltyService
from backend.utils.sanitization import sanitize_input
from backend.auth.permissions import admin_required, staff_required, roles_required, permissions_required
from ..utils.decorators import log_admin_action

loyalty_management_bp = Blueprint('loyalty_management_bp', __name__, url_prefix='/admin/loyalty')

# --- Loyalty Program Settings ---

@loyalty_management_bp.route('/settings', methods=['GET'])
@permissions_required('MANAGE_LOYALTY_PROGRAM')
@log_admin_action
@roles_required ('Admin', 'Manager')
@admin_required
def get_loyalty_settings():
    """
    Get the current settings for the loyalty program.
    """
    try:
        settings = LoyaltyService.get_settings()
        return jsonify(status="success", data=settings), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="Failed to retrieve loyalty settings."), 500

@loyalty_management_bp.route('/settings', methods=['PUT'])
@permissions_required('MANAGE_LOYALTY_PROGRAM')
@log_admin_action
@roles_required ('Admin', 'Manager')
@admin_required
def update_loyalty_settings():
    """
    Update the settings for the loyalty program.
    e.g., points per dollar, reward thresholds.
    """
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

@loyalty_management_bp.route('/users/<int:user_id>/points', methods=['POST'])
@permissions_required('MANAGE_LOYALTY_PROGRAM')
@log_admin_action
@roles_required ('Admin', 'Manager')
@admin_required
def adjust_user_points(user_id):
    """
    Manually add or remove loyalty points for a specific user.
    """
    data = request.get_json()
    if not data or 'points' not in data or 'reason' not in data:
        return jsonify(status="error", message="'points' (integer) and 'reason' (string) are required."), 400

    try:
        points = int(sanitize_input(data['points']))
        reason = sanitize_input(data['reason'])

        # Service should log this manual adjustment for auditing purposes
        updated_balance = LoyaltyService.adjust_points(user_id, points, reason)
        return jsonify(status="success", data={'new_balance': updated_balance}), 200
    except ValueError as e: # User not found, etc.
        return jsonify(status="error", message=str(e)), 404
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="Failed to adjust user points."), 500
