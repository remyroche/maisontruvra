from flask import Blueprint, jsonify, request
from backend.services.order_service import OrderService
from backend.services.exceptions import NotFoundException
from backend.auth.permissions import admin_required

order_routes = Blueprint('admin_order_routes', __name__)

@order_routes.route('/orders', methods=['GET'])
@admin_required
def get_all_orders():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    orders_page = OrderService.get_all_orders(page, per_page)
    
    return jsonify({
        "orders": [order.to_dict() for order in orders_page.items],
        "total": orders_page.total,
        "pages": orders_page.pages,
        "current_page": orders_page.page
    })

@order_routes.route('/orders/<int:order_id>', methods=['GET'])
@admin_required
def get_order_detail(order_id):
    try:
        order = OrderService.get_order_details(order_id)
        return jsonify(order.to_dict_detailed()), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404

@order_routes.route('/orders/<int:order_id>/status', methods=['PUT'])
@admin_required
def update_order_status(order_id):
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({"error": "Status is required."}), 400
        
    try:
        order = OrderService.update_order_status(order_id, new_status)
        return jsonify(order.to_dict()), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e: # For invalid status
        return jsonify({"error": str(e)}), 400