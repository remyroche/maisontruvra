from flask import Blueprint, jsonify, request
from backend.services.audit_log_service import AuditLogService
from backend.auth.permissions import admin_required

audit_log_routes = Blueprint('audit_log_routes', __name__)

@audit_log_routes.route('/audit-logs', methods=['GET'])
@admin_required
def get_audit_logs():
    """
    Retrieves a paginated list of audit logs.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    logs_page = AuditLogService.get_all_logs(page, per_page)
    
    return jsonify({
        "logs": [log.to_dict() for log in logs_page.items],
        "total": logs_page.total,
        "pages": logs_page.pages,
        "current_page": logs_page.page
    })
