from flask import Blueprint, jsonify, request
from backend.services.audit_log_service import AuditLogService
from backend.auth.permissions import admin_required, staff_required, roles_required, permissions_required
from ..utils.decorators import log_admin_action

audit_log_bp = Blueprint('admin_audit_log_routes', __name__, url_prefix='/api/admin/audit-log')

@audit_log_bp.route('/', methods=['GET'])
@log_admin_action
@roles_required ('Admin', 'Dev', 'Manager')
@admin_required
def get_audit_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    date_filter = request.args.get('date', None, type=str)
    
    logs_data = AuditLogService.get_logs(page=page, per_page=per_page, date_filter=date_filter)
    return jsonify(logs_data)
