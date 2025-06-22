from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from backend.auth.permissions import permission_required, Permission
from backend.models.order_models import Order
from backend.models.user_models import User
from backend.models.product_models import Product

dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
@permission_required(Permission.VIEW_DASHBOARD)
def dashboard_stats():
    # Example stats. You would build more complex queries for real stats.
    total_sales = db.session.query(db.func.sum(Order.total_price)).scalar()
    user_count = User.query.count()
    product_count = Product.query.count()
    
    return jsonify({
        'total_sales': total_sales or 0,
        'user_count': user_count,
        'product_count': product_count
    })


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
