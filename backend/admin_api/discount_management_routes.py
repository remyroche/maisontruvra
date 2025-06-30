# backend/admin_api/discount_management_routes.py

from flask import Blueprint, request, jsonify, g
from ..services.discount_service import DiscountService
from ..utils.decorators import api_resource_handler
from ..models import Discount
from ..schemas import DiscountCreateSchema, DiscountUpdateSchema

discount_management_bp = Blueprint('discount_management_bp', __name__, url_prefix='/admin/discounts')
discount_service = DiscountService()

@discount_management_bp.route('', methods=['POST'])
@api_resource_handler(
    model=Discount,
    schema=DiscountCreateSchema(),
    role_required='admin',
    action_log="Created Discount"
)
def create_discount():
    """Admin endpoint to create a new discount with flexible rules."""
    new_discount = discount_service.create_discount(g.validated_data)
    return jsonify(new_discount.to_dict()), 201

@discount_management_bp.route('', methods=['GET'])
@api_resource_handler(model=Discount, role_required='admin')
def get_discounts():
    """Admin endpoint to get all discounts."""
    discounts = Discount.query.all()
    return jsonify([d.to_dict() for d in discounts])

@discount_management_bp.route('/<int:discount_id>', methods=['PUT'])
@api_resource_handler(
    model=Discount,
    schema=DiscountUpdateSchema(),
    role_required='admin',
    action_log=lambda d: f"Updated Discount '{d.code}'"
)
def update_discount(discount_id):
    """Admin endpoint to update a discount."""
    updated_discount = discount_service.update_discount(g.discount, g.validated_data)
    return jsonify(updated_discount.to_dict())

@discount_management_bp.route('/<int:discount_id>', methods=['DELETE'])
@api_resource_handler(
    model=Discount,
    role_required='admin',
    action_log=lambda d: f"Deleted Discount '{d.code}'"
)
def delete_discount(discount_id):
    """Admin endpoint to delete a discount."""
    discount_service.delete_discount(g.discount)
    return jsonify({"message": "Discount deleted successfully."})
