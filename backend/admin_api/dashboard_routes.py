"""
Dashboard API routes for admin panel.
"""

from flask import Blueprint, jsonify, request
from backend.services.dashboard_service import DashboardService
from backend.utils.decorators import roles_required
import logging

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('admin_dashboard', __name__, url_prefix='/api/admin/dashboard')


@dashboard_bp.route('/stats', methods=['GET'])
@roles_required('Admin', 'Manager')
def get_dashboard_stats():
    """
    Get comprehensive dashboard statistics.
    ---
    tags:
      - Admin Dashboard
    parameters:
      - in: query
        name: days
        schema:
          type: integer
          default: 30
        description: Number of days to include in statistics
    security:
      - cookieAuth: []
    responses:
      200:
        description: Dashboard statistics retrieved successfully
      500:
        description: Error retrieving statistics
    """
    try:
        days = request.args.get('days', 30, type=int)
        dashboard_service = DashboardService(logger)
        result = dashboard_service.get_dashboard_stats(days)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error in dashboard stats endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to retrieve dashboard statistics"
        }), 500


@dashboard_bp.route('/recent-orders', methods=['GET'])
@roles_required('Admin', 'Manager')
def get_recent_orders():
    """
    Get recent orders for dashboard.
    ---
    tags:
      - Admin Dashboard
    parameters:
      - in: query
        name: limit
        schema:
          type: integer
          default: 10
        description: Maximum number of orders to return
    security:
      - cookieAuth: []
    responses:
      200:
        description: Recent orders retrieved successfully
      500:
        description: Error retrieving orders
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        dashboard_service = DashboardService(logger)
        orders = dashboard_service.get_recent_orders(limit)
        
        return jsonify({
            "success": True,
            "orders": orders
        })
        
    except Exception as e:
        logger.error(f"Error in recent orders endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to retrieve recent orders"
        }), 500