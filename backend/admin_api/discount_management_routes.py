# backend/admin_api/discount_management_routes.py

from flask import Blueprint, request, jsonify, g
from ..services.discount_service import DiscountService
from ..utils.decorators import api_resource_handler
from ..models import Discount
from backend.utils.decorators import admin_required, roles_required
from backend.services.discount_service import DiscountService
from marshmallow import ValidationError
from backend.schemas import DiscountSchema, DiscountCreateSchema, DiscountUpdateSchema

discount_management_bp = Blueprint('discount_management_bp', __name__, url_prefix='/admin/discounts')
discount_service = DiscountService()

@discount_management_bp.route('', methods=['POST'])
@roles_required('Admin', 'Manager', 'Marketing')
def create_discount():
    """ Create a new discount/coupon. """
    schema = DiscountSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    discount_service = DiscountService()
    try:
        discount = discount_service.create_discount(data)
        return jsonify({"message": "Discount created successfully.", "discount": discount.to_dict()}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 409 # e.g., code already exists
    except Exception as e:
        return jsonify({"error": "Failed to create discount."}), 500


@discount_management_bp.route('', methods=['GET'])
@api_resource_handler(model=Discount, role_required='admin')
def get_discounts():
    """Admin endpoint to get all discounts."""
    discounts = Discount.query.all()
    return jsonify([d.to_dict() for d in discounts])

@discount_management_bp.route('/<int:discount_id>', methods=['PUT'])
@roles_required('Admin', 'Manager', 'Marketing')
def update_discount(discount_id):
    """ Update an existing discount. """
    schema = DiscountSchema()
    try:
        data = schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400

    discount_service = DiscountService()
    try:
        discount = discount_service.update_discount(discount_id, data)
        if not discount:
            return jsonify({"error": "Discount not found."}), 404
        return jsonify({"message": "Discount updated successfully.", "discount": discount.to_dict()})
    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        return jsonify({"error": "Failed to update discount."}), 500



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
