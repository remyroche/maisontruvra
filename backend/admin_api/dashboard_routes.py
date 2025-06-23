from flask import Blueprint, jsonify
from backend.auth.permissions import admin_required
from backend.services.dashboard_service import DashboardService # Assumed service

admin_dashboard_bp = Blueprint('admin_dashboard_bp', __name__, url_prefix='/admin/dashboard')

@admin_dashboard_bp.route('/stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """
    Get key statistics for the main admin dashboard.
    This is a high-level overview of the entire platform's performance.
    """
    try:
        # This service method aggregates key platform-wide data.
        # e.g., total sales, new customers, pending orders, etc.
        stats = DashboardService.get_platform_stats()
        if stats is None:
            return jsonify(status="error", message="Could not retrieve platform statistics."), 500
            
        return jsonify(status="success", data=stats), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal error occurred while fetching dashboard stats."), 500

@admin_dashboard_bp.route('/recent-activity', methods=['GET'])
@admin_required
def get_recent_activity():
    """
    Get a feed of recent activities across the platform for the admin dashboard.
    """
    try:
        # This service method fetches a list of recent, significant events.
        # e.g., new orders, new user registrations, high-value purchases.
        limit = request.args.get('limit', 10, type=int)
        activity = DashboardService.get_recent_activity(limit=limit)
        
        # The to_dict method for each activity should be carefully crafted 
        # to provide a useful summary for the dashboard.
        return jsonify(status="success", data=[item.to_dict() for item in activity]), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal error occurred while fetching recent activity."), 500

