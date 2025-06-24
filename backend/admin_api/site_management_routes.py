from flask import Blueprint, request, jsonify
from backend.services.site_settings_service import SiteSettingsService # Assumed service
from backend.utils.sanitization import sanitize_input
from backend.auth.permissions import permissions_required
from backend.auth.permissions import admin_required, staff_required, roles_required, permissions_required
from ..utils.decorators import log_admin_action

site_management_bp = Blueprint('site_management_bp', __name__, url_prefix='/admin/site-settings')

# READ all site settings
@site_management_bp.route('/', methods=['GET'])
@permissions_required('MANAGE_SITE_SETTINGS')
@log_admin_action
@roles_required ('Admin', 'Dev')
@admin_required
def get_site_settings():
    """
    Retrieve all site settings.
    """
    try:
        settings = SiteSettingsService.get_all_settings()
        return jsonify(status="success", data=settings), 200
    except Exception as e:
        # Proper logging should be implemented here
        return jsonify(status="error", message="An internal error occurred while fetching site settings."), 500

# UPDATE site settings
@site_management_bp.route('/', methods=['PUT'])
@permissions_required('MANAGE_SITE_SETTINGS')
@log_admin_action
@roles_required ('Admin', 'Dev')
@admin_required
def update_site_settings():
    """
    Update one or more site settings.
    Expects a JSON object where keys are the setting names and values are the new values.
    """
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify(status="error", message="Invalid or missing JSON object in request body"), 400

    # Sanitize all incoming values
    sanitized_data = sanitize_input(data)

    try:
        updated_settings = SiteSettingsService.update_settings(sanitized_data)
        return jsonify(status="success", message="Site settings updated successfully.", data=updated_settings), 200
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Proper logging should be implemented here
        return jsonify(status="error", message="An internal error occurred while updating site settings."), 500

