from backend.services.b2b_service import B2BService
from backend.auth.permissions import b2b_user_required
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from services.dashboard_service import B2BDashboardService
from utils.auth_helpers import b2b_required
from utils.sanitization import sanitize_input

b2b_dashboard_bp = Blueprint('b2b_dashboard_bp', __name__, url_prefix='/api/b2b/dashboard')
dashboard_service = B2BDashboardService()

@b2b_dashboard_bp.route('/stats', methods=['GET'])
@b2b_required
def get_b2b_dashboard_stats():
    period = sanitize_input(request.args.get('period', '30d'))
    stats = dashboard_service.get_b2b_stats(current_user.id, period)
    return jsonify(stats)

@b2b_dashboard_bp.route('/recent-orders', methods=['GET'])
@b2b_required
def get_b2b_recent_orders():
    limit = request.args.get('limit', 5, type=int)
    orders = dashboard_service.get_recent_orders(current_user.id, limit)
    return jsonify([order.to_dict() for order in orders])

@b2b_dashboard_bp.route('/top-products', methods=['GET'])
@b2b_required
def get_b2b_top_products():
    limit = request.args.get('limit', 5, type=int)
    products = dashboard_service.get_top_products(current_user.id, limit)
    return jsonify(products)

@b2b_dashboard_bp.route('/quote-requests', methods=['GET'])
@b2b_required
def get_b2b_quote_requests():
    limit = request.args.get('limit', 5, type=int)
    quotes = dashboard_service.get_recent_quote_requests(current_user.id, limit)
    return jsonify([quote.to_dict() for quote in quotes])

@b2b_dashboard_bp.route('/stats', methods=['GET'])
@b2b_user_required
def get_dashboard_stats():
    """
    Get key statistics for the B2B user's dashboard.
    """
    user_id = get_jwt_identity()
    try:
        # This service method should be implemented to aggregate dashboard data
        # for the specific B2B user.
        stats = B2BService.get_dashboard_stats(user_id)
        if stats is None:
            return jsonify(status="error", message="Could not retrieve dashboard statistics."), 500
            
        return jsonify(status="success", data=stats), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal error occurred while fetching dashboard stats."), 500
