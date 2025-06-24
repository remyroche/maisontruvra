from flask import Blueprint, request, jsonify
from services.audit_log_service import AuditLogService
from backend.auth.permissions import admin_required, staff_required, roles_required, permissions_required
from ..utils.decorators import log_admin_action
from utils.sanitization import sanitize_input

admin_audit_log_bp = Blueprint('admin_audit_log_bp', __name__)
audit_log_service = AuditLogService()

@admin_audit_log_bp.route('/', methods=['GET'])
@log_admin_action
@roles_required ('Admin', 'Dev', 'Manager')
@admin_requireddef get_audit_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = sanitize_input(request.args.get('user_id'))
    action_type = sanitize_input(request.args.get('action_type'))
    start_date = sanitize_input(request.args.get('start_date'))
    end_date = sanitize_input(request.args.get('end_date'))
    sort_by = sanitize_input(request.args.get('sort_by', 'timestamp'))
    sort_direction = sanitize_input(request.args.get('sort_direction', 'desc'))

    logs = audit_log_service.get_logs(
        page=page,
        per_page=per_page,
        user_id=user_id,
        action_type=action_type,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_direction=sort_direction
    )
    
    return jsonify({
        'logs': [log.to_dict() for log in logs.items],
        'total': logs.total,
        'pages': logs.pages,
        'current_page': logs.page
    })
