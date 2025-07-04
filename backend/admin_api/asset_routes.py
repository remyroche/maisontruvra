"""
This module defines the API endpoints for asset management (file uploads)
in the admin panel. It uses a hybrid approach: a custom endpoint for uploads
and a decorator-driven endpoint for managing existing assets.
"""

from flask import Blueprint, request, g, jsonify
from ..models import Asset
from ..schemas import AssetSchema
from ..utils.decorators import api_resource_handler, roles_required
from ..services.asset_service import AssetService

# --- Blueprint Setup ---
bp = Blueprint("asset_management", __name__, url_prefix="/api/admin/assets")


@bp.route("/", methods=["GET"])
@roles_required("Admin", "Manager", "Editor")
def list_assets():
    """Handles listing and pagination of all assets."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    paginated_assets = AssetService.get_all_assets_paginated(
        page=page, per_page=per_page
    )

    return jsonify(
        {
            "data": AssetSchema(many=True).dump(paginated_assets.items),
            "total": paginated_assets.total,
            "pages": paginated_assets.pages,
            "current_page": paginated_assets.page,
        }
    )


@bp.route("/", methods=["POST"])
@roles_required("Admin", "Manager", "Editor")
def upload_asset():
    """
    Handles file uploads. This endpoint uses multipart/form-data,
    so it does not use the standard JSON-based decorator.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file:
        # The service layer should handle the logic for saving the file
        # to a cloud storage provider (like S3) and creating the DB record.
        asset = AssetService.upload_asset(file)
        return jsonify(AssetSchema().dump(asset)), 201

    return jsonify({"error": "File upload failed"}), 500


@bp.route("/<int:asset_id>", methods=["GET", "DELETE"])
@roles_required("Admin", "Manager", "Editor")
@api_resource_handler(
    model=Asset,
    response_schema=AssetSchema,
    log_action=True,
    allow_hard_delete=True,  # Assets can be permanently deleted
)
def handle_single_asset(asset_id=None, is_hard_delete=False):
    """
    Handles viewing and deleting a single asset.
    """
    if request.method == "GET":
        # The decorator fetches the asset and places it in g.target_object.
        return g.target_object

    elif request.method == "DELETE":
        # The decorator ensures hard delete is allowed.
        # The service layer should handle deleting the file from cloud storage.
        AssetService.delete_asset(asset_id)
        return None  # Decorator provides the success message.
