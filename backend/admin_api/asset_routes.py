from flask import request, jsonify
from . import admin_api_bp # Assuming this is your admin blueprint
from ..services.asset_service import AssetService
from ..services.exceptions import ServiceError, NotFoundException
from backend.auth.permissions import admin_required, staff_required, roles_required, permissions_required
from ..utils.decorators import log_admin_action

@admin_api_bp.route('/assets/upload', methods=['POST'])
@log_admin_action
@roles_required('Admin', 'Manager', 'Editor')
@admin_required
def upload_asset():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    usage_tag = request.form.get('usage_tag')

    try:
        asset = AssetService.upload_asset(file, usage_tag)
        return jsonify(asset.to_dict()), 201
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status_code

@admin_api_bp.route('/assets', methods=['GET'])
@log_admin_action
@roles_required('Admin', 'Manager', 'Editor')
@admin_required
def get_assets():
    assets = AssetService.get_all_assets()
    return jsonify([asset.to_dict() for asset in assets])

@admin_api_bp.route('/assets/<int:asset_id>', methods=['DELETE'])
@log_admin_action
@roles_required('Admin', 'Manager', 'Editor')
@admin_required
def delete_asset(asset_id):
    try:
        AssetService.delete_asset(asset_id)
        return '', 204
    except NotFoundException as e:
        return jsonify({"error": e.message}), 404
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status_code
