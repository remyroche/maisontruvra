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
    """
    Retrieves audit log entries with optional filtering.
    """
    admin_id = request.args.get('admin_id')
    logs = AuditLogService.get_logs(admin_id=admin_id)
    return jsonify([log.to_dict() for log in logs])
