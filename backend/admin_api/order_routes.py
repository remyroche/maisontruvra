from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from backend.models.order_models import Order
from backend.extensions import db
from backend.auth.permissions import permission_required, Permission

order_bp = Blueprint('admin_order_bp', __name__, url_prefix='/orders')

@order_bp.route('/', methods=['GET'])
@jwt_required()
@permission_required(Permission.MANAGE_ORDERS)
def get_all_orders():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    orders = Order.query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "orders": [order.to_dict() for order in orders.items],
        "total": orders.total,
        "pages": orders.pages,
        "current_page": orders.page
    })

@order_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
@permission_required(Permission.MANAGE_ORDERS)
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict_detailed())

@order_bp.route('/<int:order_id>/status', methods=['PUT'])
@jwt_required()
@permission_required(Permission.MANAGE_ORDERS)
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    new_status = data.get('status')

    if not new_status:
        return jsonify({"msg": "Status is required"}), 400

    # You might want to add more validation for allowed statuses
    order.status = new_status
    db.session.commit()
    
    return jsonify({"msg": f"Order {order_id} status updated to {new_status}"})
    
