from flask import Blueprint, jsonify
from backend.auth.permissions import b2b_user_required
from flask_jwt_extended import get_jwt_identity
from backend.services.user_service import UserService
from backend.services.order_service import OrderService

dashboard_routes = Blueprint('b2b_dashboard_routes', __name__)

@dashboard_routes.route('/dashboard', methods=['GET'])
@b2b_user_required
def get_b2b_dashboard_data():
    """
    Get dashboard data for the logged-in B2B user.
    """
    user_id = get_jwt_identity()
    user = UserService.get_user_by_id(user_id)
    b2b_user = user.b2b_account[0]
    
    # Example data aggregation
    recent_orders = OrderService.get_orders_by_user(user_id, limit=5)
    
    dashboard_data = {
        "company_name": b2b_user.company_name,
        "recent_orders": [order.to_dict() for order in recent_orders],
        "total_spent": sum(o.total_amount for o in user.orders if o.status == 'COMPLETED')
    }
    
    return jsonify(dashboard_data), 200