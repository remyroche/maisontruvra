from flask import Blueprint, jsonify, request
from backend.services.recycling_bin_service import RecyclingBinService
from backend.utils.decorators import admin_required

recycling_bin_bp = Blueprint('recycling_bin_bp', __name__, url_prefix='/api/admin/recycling-bin')

recycling_bin_service = RecyclingBinService()

@recycling_bin_bp.route('/', methods=['GET'])
@admin_required
def get_soft_deleted():
    """
    API endpoint to get all soft-deleted items.
    """
    try:
        items = recycling_bin_service.get_soft_deleted_items()
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recycling_bin_bp.route('/restore', methods=['POST'])
@admin_required
def restore_item():
    """
    API endpoint to restore a soft-deleted item.
    Expects JSON payload with 'item_type' and 'item_id'.
    """
    data = request.get_json()
    item_type = data.get('item_type')
    item_id = data.get('item_id')

    if not item_type or not item_id:
        return jsonify({"error": "Missing item_type or item_id"}), 400

    try:
        recycling_bin_service.restore_item(item_type, item_id)
        return jsonify({"message": f"{item_type} with ID {item_id} restored successfully."}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recycling_bin_bp.route('/hard-delete', methods=['DELETE'])
@admin_required
def hard_delete_item():
    """
    API endpoint to permanently delete an item.
    Expects JSON payload with 'item_type' and 'item_id'.
    """
    data = request.get_json()
    item_type = data.get('item_type')
    item_id = data.get('item_id')

    if not item_type or not item_id:
        return jsonify({"error": "Missing item_type or item_id"}), 400

    try:
        recycling_bin_service.hard_delete_item(item_type, item_id)
        return jsonify({"message": f"{item_type} with ID {item_id} permanently deleted."}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recycling_bin_bp.route('/logs', methods=['GET'])
@admin_required
def get_logs():
    """
    API endpoint to get deletion logs for a specific item.
    Expects query parameters 'item_type' and 'item_id'.
    """
    item_type = request.args.get('item_type')
    item_id = request.args.get('item_id')

    if not item_type or not item_id:
        return jsonify({"error": "Missing item_type or item_id query parameters"}), 400

    try:
        logs = recycling_bin_service.get_deletion_logs(item_type, int(item_id))
        return jsonify(logs), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
