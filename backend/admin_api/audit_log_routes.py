from flask import Blueprint, jsonify, request
from backend.services.audit_log_service import AuditLogService
from backend.utils.decorators import staff_required, roles_required, permissions_required

audit_log_bp = Blueprint('admin_audit_log_routes', __name__, url_prefix='/api/admin/audit-log')

@audit_log_bp.route('/', methods=['GET'])
@roles_required ('Admin', 'Dev', 'Manager')
def get_audit_logs():
    """
    Retrieves a paginated and filterable list of audit log entries.
    This is a read-only endpoint for security and compliance review.
    C[R]UD - Read (List)
    """
    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    # Filtering parameters (all sanitized)
    user_id_filter = sanitize_input(request.args.get('user_id', type=int))
    action_filter = sanitize_input(request.args.get('action', type=str))

    # Build the query
    query = AdminAuditLog.query.options(joinedload(AdminAuditLog.user)).order_by(AdminAuditLog.timestamp.desc())

    if user_id_filter:
        query = query.filter(AdminAuditLog.user_id == user_id_filter)
    
    if action_filter:
        query = query.filter(AdminAuditLog.action.ilike(f"%{action_filter}%"))

    logs_page = query.paginate(page=page, per_page=per_page, error_out=False)

    # Format data for frontend compatibility
    return jsonify({
        "logs": [log.to_dict() for log in logs_page.items],
        "total": logs_page.total,
        "page": logs_page.page,
        "pages": logs_page.pages
    })
