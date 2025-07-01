"""
This module defines the API endpoints for inventory management in the admin panel.
"""
from flask import Blueprint, request, g, jsonify
from ..models import Inventory
from ..schemas import InventoryUpdateSchema
from ..utils.decorators import api_resource_handler, roles_required
from ..services.inventory_service import InventoryService

bp = Blueprint('inventory_management', __name__, url_prefix='/api/admin/inventory')

@bp.route('/<int:inventory_id>', methods=['PUT'])
@roles_required('Admin', 'Manager', 'Farmer')
@api_resource_handler(
    model=Inventory, 
    request_schema=InventoryUpdateSchema
)
def update_inventory(inventory_id):
    """Updates inventory quantity and triggers back-in-stock notifications."""
    inventory_item = g.target_object
    new_quantity = g.validated_data['quantity']
    
    InventoryService.update_stock_and_notify(inventory_item, new_quantity)
    
    return jsonify(message=f"Inventory for product {inventory_item.product_id} updated.")
