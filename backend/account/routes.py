from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.user_service import UserService
from backend.services.order_service import OrderService
from backend.services.exceptions import ServiceException

account_bp = Blueprint('account_bp', __name__)

@account_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    try:
        user = UserService.get_user_by_id(user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404
        return jsonify(user.to_dict()), 200
    except ServiceException as e:
        return jsonify({"msg": str(e)}), 500

@account_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json()
    try:
        updated_user = UserService.update_user(user_id, data)
        return jsonify(updated_user.to_dict()), 200
    except ServiceException as e:
        return jsonify({"msg": str(e)}), 400

@account_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_user_orders():
    user_id = get_jwt_identity()
    try:
        orders = OrderService.get_orders_by_user(user_id)
        return jsonify([order.to_dict() for order in orders]), 200
    except ServiceException as e:
        return jsonify({"msg": str(e)}), 500

@account_bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_user_order_detail(order_id):
    user_id = get_jwt_identity()
    try:
        order = OrderService.get_order_details(order_id, user_id)
        if not order:
             return jsonify({"msg": "Order not found or access denied"}), 404
        return jsonify(order.to_dict_detailed()), 200
    except ServiceException as e:
        return jsonify({"msg": str(e)}), 500

