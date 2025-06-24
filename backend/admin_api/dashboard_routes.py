from flask import Blueprint, jsonify, request
from ..utils.decorators import admin_required, staff_required, roles_required, permissions_required
from ..utils.decorators import log_admin_action
# Import the new, fully implemented service
from backend.services.admin_dashboard_service import AdminDashboardService

admin_dashboard_bp = Blueprint('admin_dashboard_bp', __name__, url_prefix='/admin/dashboard')

@admin_dashboard_bp.route('/stats', methods=['GET'])
@log_admin_action
@roles_required ('Admin', 'Manager', 'Dev')
@admin_required
def get_dashboard_stats():
    """
    Get key statistics for the main admin dashboard.
    This is a high-level overview of the entire platform's performance.
    """
    try:
        stats = AdminDashboardService.get_platform_stats()
        return jsonify(status="success", data=stats), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal error occurred while fetching dashboard stats."), 500

@admin_dashboard_bp.route('/recent-activity', methods=['GET'])
@log_admin_action
@roles_required ('Admin', 'Manager', 'Dev')
@admin_required
def get_recent_activity():
    """
    Get a feed of recent activities across the platform for the admin dashboard.
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        activity = AdminDashboardService.get_recent_activity(limit=limit)
        
        return jsonify(status="success", data=activity), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal error occurred while fetching recent activity."), 500
