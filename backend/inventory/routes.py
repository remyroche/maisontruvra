from flask import Blueprint, jsonify, request
from backend.services.inventory_service import InventoryService # Assumed service
from backend.utils.decorators import permissions_required, admin_required
from backend.utils.input_sanitizer import InputSanitizer
from backend.services import product_service

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


@inventory_bp.route('/update', methods=['POST'])
@admin_required
def update_inventory_levels():
    data = InputSanitizer.sanitize_input(request.get_json())
    # data format: [{'product_id': 1, 'quantity': 100}, ...]
    try:
        product_service.update_inventory_levels(data)
        return jsonify({'message': 'Inventory levels updated successfully.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
