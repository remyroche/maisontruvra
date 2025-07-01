"""
This module defines the API endpoints for discount management in the admin panel.
It leverages the @api_resource_handler to create clean, secure, and consistent CRUD endpoints.
"""
from flask import Blueprint, request, g, jsonify
from ..models import Discount
from ..schemas import DiscountSchema
from ..utils.decorators import api_resource_handler, roles_required
from ..services.discount_service import DiscountService

# --- Blueprint Setup ---
bp = Blueprint('discount_management', __name__, url_prefix='/api/admin/discounts')

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/<int:discount_id>', methods=['GET', 'PUT', 'DELETE'])
@roles_required('Admin', 'Manager')
@api_resource_handler(
    model=Discount,
    request_schema=DiscountSchema,
    response_schema=DiscountSchema,
    log_action=True,
    allow_hard_delete=False # Soft delete is the safe default for discounts
)
def handle_discounts(discount_id=None, is_hard_delete=False):
    """Handles all CRUD operations for Discounts."""
    
    # Handle the collection GET request for all discounts
    if request.method == 'GET' and discount_id is None:
        all_discounts = DiscountService.get_all_discounts()
        return jsonify(DiscountSchema(many=True).dump(all_discounts))

    # --- Single Discount Operations ---
    # The decorator handles fetching the discount and validating data.

    if request.method == 'GET':
        # g.target_object is the discount fetched by the decorator.
        return g.target_object

    elif request.method == 'POST':
        # g.validated_data contains the sanitized and validated discount data.
        return DiscountService.create_discount(g.validated_data)

    elif request.method == 'PUT':
        # g.target_object is the discount to update.
        # g.validated_data contains the new data.
        return DiscountService.update_discount(g.target_object, g.validated_data)

    elif request.method == 'DELETE':
        # The decorator ensures is_hard_delete is False by default.
        if is_hard_delete:
            DiscountService.hard_delete_discount(discount_id)
        else:
            # Safe, default behavior.
            DiscountService.soft_delete_discount(discount_id)
        return None # Decorator provides the success message.
