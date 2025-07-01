from flask import Blueprint, jsonify, request
from backend.utils.decorators import roles_required, permissions_required
from backend.services.site_settings_service import SiteSettingsService
from marshmallow import ValidationError
from backend.schemas import SiteSettingsSchema


site_management_bp = Blueprint('admin_site_management_routes', __name__, url_prefix='/api/admin/site-settings')

@site_management_bp.route('/', methods=['GET'])
@admin_required
def get_site_settings():
    """ Get all site settings. """
    settings_service = SiteSettingsService()
    settings = settings_service.get_all_settings()
    return jsonify(settings)

@site_management_bp.route('/', methods=['PUT'])
@admin_required
def update_site_settings():
    """ Update site settings. """
    schema = SiteSettingsSchema()
    try:
        # The schema can validate known fields, and unknown=INCLUDE allows other settings
        # request.json is automatically sanitized by middleware
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    settings_service = SiteSettingsService()
    try:
        settings_service.update_settings(data)
        return jsonify({"message": "Site settings updated successfully."})
    except Exception as e:
        return jsonify({"error": "Failed to update settings."}), 500
