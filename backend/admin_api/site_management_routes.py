from flask import Blueprint, request, jsonify
from backend.services.settings_service import SettingsService
from backend.auth.permissions import admin_required

site_management_routes = Blueprint('site_management_routes', __name__)

@site_management_routes.route('/settings', methods=['GET'])
@admin_required
def get_site_settings():
    settings = SettingsService.get_all_settings()
    return jsonify(settings), 200

@site_management_routes.route('/settings', methods=['POST'])
@admin_required
def update_site_settings():
    settings_data = request.get_json()
    try:
        SettingsService.update_settings(settings_data)
        return jsonify({"message": "Settings updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update settings: {str(e)}"}), 500

@site_management_routes.route('/maintenance-mode', methods=['POST'])
@admin_required
def toggle_maintenance_mode():
    data = request.get_json()
    is_enabled = data.get('enabled', False)
    SettingsService.set_setting('maintenance_mode', is_enabled)
    return jsonify({"message": f"Maintenance mode {'enabled' if is_enabled else 'disabled'}."})
