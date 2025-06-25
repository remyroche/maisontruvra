from flask import Blueprint, jsonify
from backend.services.admin_dashboard_service import AdminDashboardService
from backend.auth.permissions import admin_required, staff_required, roles_required, permissions_required
from ..utils.decorators import log_admin_action

dashboard_bp = Blueprint('admin_dashboard_routes', __name__, url_prefix='/api/admin/dashboard')

@dashboard_bp.route('/stats', methods=['GET'])
@admin_dashboard_bp.route('/stats', methods=['GET'])
@log_admin_action
@roles_required ('Admin', 'Manager', 'Dev')
@admin_required
def get_dashboard_stats():
    """
    Retrieves key statistics for the admin dashboard.
    """
    stats = AdminDashboardService.get_dashboard_statistics()
    return jsonify(stats)

@dashboard_bp.route('/recent-activity', methods=['GET'])
@admin_dashboard_bp.route('/stats', methods=['GET'])
@log_admin_action
@roles_required ('Admin', 'Manager', 'Dev')
@admin_required
def get_recent_activity():
    """
    Retrieves recent activities for the admin dashboard.
    """
    activity = AdminDashboardService.get_recent_activity()
    return jsonify(activity)

