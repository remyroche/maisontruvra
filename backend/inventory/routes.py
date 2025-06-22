from flask import Blueprint, jsonify
from backend.services.inventory_service import InventoryService
from backend.auth.permissions import admin_required

inventory_bp = Blueprint('inventory_routes', __name__)

@inventory_bp.route('/status', methods=['GET'])
@admin_required
def get_inventory_status():
    """
    Get the inventory status for all products.
    """
    inventory_list = InventoryService.get_full_inventory_report()
    return jsonify(inventory_list), 200

@inventory_bp.route('/status/<string:sku>', methods=['GET'])
def get_product_stock(sku):
    """
    Get the stock level for a specific product by SKU.
    This might be a public or internal endpoint.
    For now, let's assume it's public.
    """
    stock_level = InventoryService.get_stock_by_sku(sku)
    if stock_level is None:
        return jsonify({"error": "Product not found"}), 404
    return jsonify({"sku": sku, "stock_level": stock_level}), 200
