from flask import Blueprint, jsonify
from backend.services.dashboard_service import DashboardService
from backend.auth.permissions import admin_required

dashboard_routes = Blueprint('dashboard_routes', __name__)

@dashboard_routes.route('/dashboard/stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    stats = DashboardService.get_main_stats()
    return jsonify(stats), 200

@dashboard_routes.route('/dashboard/sales-over-time', methods=['GET'])
@admin_required
def get_sales_over_time():
    period = request.args.get('period', 'week') # e.g., week, month, year
    data = DashboardService.get_sales_over_time(period)
    return jsonify(data), 200

@dashboard_routes.route('/dashboard/top-products', methods=['GET'])
@admin_required
def get_top_products():
    limit = request.args.get('limit', 5, type=int)
    data = DashboardService.get_top_selling_products(limit)
    return jsonify(data), 200
