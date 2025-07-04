"""
This module defines the API endpoints for managing global site settings.
"""

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from ..extensions import db
from ..schemas import SiteSettingsSchema
from ..services.site_settings_service import SiteSettingsService
from ..utils.decorators import roles_required

# --- Blueprint Setup ---
bp = Blueprint("site_management", __name__, url_prefix="/api/admin/site-settings")


@bp.route("/", methods=["GET"])
@roles_required("Admin", "Manager")
def get_site_settings():
    """
    Retrieves all site settings from the database.
    This endpoint uses a cached service method for performance.
    """
    settings = SiteSettingsService.get_all_settings_cached()
    return jsonify(settings)


@bp.route("/", methods=["PUT"])
@roles_required("Admin", "Manager")
def update_site_settings():
    """
    Updates multiple site settings in a single transaction.
    The request body should be a JSON object containing the settings.
    Example: { "settings": { "site_name": "Maison Truvra", "maintenance_mode": "false" } }
    """
    # Manually handle validation and transaction since this isn't a standard CRUD resource.
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Invalid JSON data provided"}), 400

    try:
        # Validate the incoming data against our schema
        validated_data = SiteSettingsSchema().load(json_data)

        # The service layer handles the update logic and cache invalidation
        SiteSettingsService.update_settings(validated_data["settings"])

        # The service commits the session, so we don't need to do it here.

        return jsonify({"message": "Site settings updated successfully."}), 200

    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        # Log the error properly in a real application
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500
