from backend.services.b2b_service import B2BService
from backend.auth.permissions import b2b_user_required

b2b_dashboard_bp = Blueprint('b2b_dashboard_bp', __name__, url_prefix='/api/b2b/dashboard')

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

@b2b_dashboard_bp.route('/recent-orders', methods=['GET'])
@b2b_user_required
def get_recent_orders():
    """
    Get a list of the most recent orders for the B2B user.
    """
    user_id = get_jwt_identity()
    try:
        # This service method should be implemented to get the most recent orders
        limit = 5 # Or get from request.args
        recent_orders = B2BService.get_recent_orders(user_id, limit=limit)
        return jsonify(status="success", data=[order.to_dict_for_user() for order in recent_orders]), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal error occurred while fetching recent orders."), 500
