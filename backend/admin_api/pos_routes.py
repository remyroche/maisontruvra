from flask import Blueprint, request, jsonify
from backend.services.order_service import OrderService
from backend.services.exceptions import ServiceException
from backend.auth.permissions import admin_required, permission_required, Permissi
from flask_jwt_extended import jwt_required
from backend.models.product_models import Product, Category, Collection
from backend.extensions import db


pos_routes = Blueprint('admin_pos_routes', __name__)

@pos_routes.route('/pos/create-order', methods=['POST'])
@admin_required
def create_pos_order():
    """
    Creates an order from a Point of Sale terminal.
    This would typically have more specific logic than a standard web order.
    """
    data = request.get_json()
    
    # The OrderService might need a specific method for POS orders
    # to handle things like in-person payment methods.
    try:
        order = OrderService.create_order_from_pos(data)
        return jsonify(order.to_dict()), 201
    except ServiceException as e:
        return jsonify({"error": str(e)}), 400
