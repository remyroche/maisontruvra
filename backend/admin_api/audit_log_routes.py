from flask import Blueprint, jsonify, request
from backend.utils.decorators import admin_required
from backend.models import AdminAuditLog
from backend.schemas import AdminAuditLogSchema

admin_audit_log_routes = Blueprint(
    "admin_audit_log_routes", __name__, url_prefix="/api/admin/audit-log"
)
from sqlalchemy.orm import joinedload  # noqa: E402


@admin_audit_log_routes.route("/", methods=["GET"])
@admin_required
def get_audit_logs():
    """
    Retrieves a paginated list of audit logs.
    Admins can filter by user_id or action.
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    user_id = request.args.get("user_id", type=int)
    action = request.args.get("action", type=str)

    logs_query = AdminAuditLog.query.options(joinedload(AdminAuditLog.user)).order_by(
        AdminAuditLog.timestamp.desc()
    )

    if user_id:
        logs_query = logs_query.filter_by(user_id=user_id)
    if action:
        logs_query = logs_query.filter_by(action=action)

    logs = logs_query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(
        {
            "logs": AdminAuditLogSchema(many=True).dump(logs.items),
            "total": logs.total,
            "pages": logs.pages,
            "current_page": logs.page,
        }
    )
