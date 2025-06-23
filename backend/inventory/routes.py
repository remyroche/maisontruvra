from flask import Blueprint, jsonify
from backend.services.inventory_service import InventoryService # Assumed service
from backend.auth.permissions import permissions_required

inventory_bp = Blueprint('inventory_bp', __name__, url_prefix='/api/inventory')

# Check stock level for a specific product
@inventory_bp.route('/stock/<int:product_id>', methods=['GET'])
@permissions_required('VIEW_INVENTORY')
def get_stock_level(product_id):
    """
    Get the current stock level for a specific product.
    Requires permission to view inventory.
    """
    try:
        stock_info = InventoryService.get_stock_for_product(product_id)
        if stock_info is None:
            return jsonify(status="error", message="Product not found in inventory."), 404
        
        return jsonify(status="success", data=stock_info), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal error occurred while fetching stock levels."), 500
