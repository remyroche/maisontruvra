# backend/admin_api/inventory_management_routes.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from ..services.inventory_service import InventoryService
from ..utils.decorators import roles_required 
from ..services.exceptions import NotFoundException, ValidationException, ServiceError

# Assuming the blueprint is named this way. If it's different, I'll adapt.
inventory_admin_bp = Blueprint('inventory_admin_bp', __name__, url_prefix='/api/admin/inventory')

# --- NEW ROUTE FOR CREATING AN ITEM ---
@inventory_admin_bp.route('/items', methods=['POST'])
@jwt_required()
@roles_required('Admin', 'Manager', 'Farmer')
def create_inventory_item():
    """
    Admin endpoint to create a new, unique inventory Item from a parent Product.
    This endpoint receives data from the ItemForm.vue component.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON data in request."}), 400

    try:
        # The InventoryService handles all the complex logic,
        # including passport and QR code generation.
        new_item = InventoryService.create_item(data)
        return jsonify(new_item.to_dict()), 201
    except (ValidationException, NotFoundException) as e:
        # Handle specific, expected errors (e.g., product not found)
        return jsonify({"error": str(e)}), 400
    except ServiceError as e:
        # Handle general service layer errors
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        # Log unexpected errors for debugging
        current_app.logger.error(f"Unexpected error creating inventory item: {e}", exc_info=True)
        return jsonify({"error": "An unexpected internal error occurred."}), 500

# --- NEW ROUTE FOR LISTING ALL ITEMS ---
@inventory_admin_bp.route('/items', methods=['GET'])
@jwt_required()
@roles_required('Admin', 'Manager', 'Farmer', 'Support')
def get_all_inventory_items():
    """
    Admin endpoint to retrieve a list of all unique inventory items.
    This will be used to populate the main inventory management view.
    """
    try:
        items = InventoryService.get_all_items()
        return jsonify([item.to_dict() for item in items]), 200
    except ServiceError as e:
        return jsonify({"error": str(e)}), 500
