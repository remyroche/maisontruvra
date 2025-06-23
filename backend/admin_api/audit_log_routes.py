from flask import Blueprint, request, jsonify
from backend.services.audit_log_service import AuditLogService  # Assumed service
from backend.auth.permissions import permissions_required

audit_log_bp = Blueprint('audit_log_bp', __name__, url_prefix='/admin/audit-log')

# READ all audit logs (with pagination and filtering)
@audit_log_bp.route('/', methods=['GET'])
@permissions_required('VIEW_AUDIT_LOG')
def get_audit_logs():
    """
    Get a paginated list of audit log entries.
    Query Params:
    - page: The page number to retrieve.
    - per_page: The number of entries per page.
    - user_id: Filter by the ID of the user who performed the action.
    - action: Filter by the type of action performed.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        filters = {
            'user_id': request.args.get('user_id', type=int),
            'action': request.args.get('action', type=str)
        }
        filters = {k: v for k, v in filters.items() if v is not None}

        logs_pagination = AuditLogService.get_all_logs_paginated(page=page, per_page=per_page, filters=filters)
        
        return jsonify({
            "status": "success",
            "data": [log.to_dict() for log in logs_pagination.items],
            "total": logs_pagination.total,
            "pages": logs_pagination.pages,
            "current_page": logs_pagination.page
        }), 200
    except Exception as e:
        # In a real app, log the error e
        return jsonify(status="error", message="An internal error occurred while fetching audit logs."), 500
