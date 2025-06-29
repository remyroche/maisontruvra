from flask import Blueprint, jsonify, request
from backend.services.site_settings_service import SiteSettingsService # Assuming this service exists
from backend.utils.decorators import roles_required, permissions_required

site_management_bp = Blueprint('admin_site_management_routes', __name__, url_prefix='/api/admin/site-settings')

@site_management_bp.route('/', methods=['GET'])
@permissions_required('MANAGE_SITE_SETTINGS')
@roles_required ('Admin', 'Dev')
def get_settings():
    """Retrieves all site settings."""
    settings = SiteSettingsService.get_all_settings()
    return jsonify(settings)

@site_management_bp.route('/', methods=['POST'])
@permissions_required('MANAGE_SITE_SETTINGS')
@roles_required ('Admin', 'Dev')
def update_settings():
    """Updates multiple site settings at once."""
    settings_data = request.get_json()
    try:
        SiteSettingsService.update_settings(settings_data)
        return jsonify({"message": "Settings updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
