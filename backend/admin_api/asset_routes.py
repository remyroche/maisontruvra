from flask import request, jsonify
from flask_login import current_user
from . import admin_api_bp # Assuming this is your admin blueprint
from ..services.asset_service import AssetService
from ..services.exceptions import ServiceError, NotFoundException
from backend.utils.decorators import staff_required, roles_required, permissions_required
from backend.services.audit_log_service import AuditLogService
from backend.extensions import limiter
@admin_api_bp.route('/assets/upload', methods=['POST'])
@roles_required('Admin', 'Manager', 'Editor')
@limiter.limit("20 per minute") # Rate limit to prevent resource exhaustion attacks
def upload_asset():
    """
    Handles file uploads from the admin panel.
    The core security logic (MIME type validation, sanitization) is in the AssetService.
    This endpoint enforces admin permissions and audits the action.
    [C]RUD - Create
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400

    try:
        # The service layer performs all necessary validation and sanitization
        result = AssetService.upload_asset(file, folder='products')
        
        # Log the successful upload action
        AuditLogService.log_action(
            user_id=current_user.id,
            action='upload_asset',
            details=f"Uploaded asset '{file.filename}'. URL: {result.get('url')}"
        )
        
        # The response format provides the URL needed by the frontend editor
        return jsonify(result), 201
        
    except Exception as e:
        # Catch exceptions from the service layer (e.g., ValidationError)
        return jsonify({"error": str(e)}), 400

@admin_api_bp.route('/assets', methods=['GET'])
@roles_required('Admin', 'Manager', 'Editor')
def get_assets():
    assets = AssetService.get_all_assets()
    return jsonify([asset.to_dict() for asset in assets])

@admin_api_bp.route('/assets/<int:asset_id>', methods=['DELETE'])
@roles_required('Admin', 'Manager', 'Editor')
def delete_asset(asset_id):
    try:
        AssetService.delete_asset(asset_id)
        return '', 204
    except NotFoundException as e:
        return jsonify({"error": e.message}), 404
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status_code
