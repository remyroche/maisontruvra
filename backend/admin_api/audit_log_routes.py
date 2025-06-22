from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from backend.models.audit_models import AuditLog
from backend.auth.permissions import permission_required, Permission

audit_log_bp = Blueprint('audit_log_bp', __name__, url_prefix='/audit-log')

@audit_log_bp.route('/', methods=['GET'])
@jwt_required()
@permission_required(Permission.VIEW_AUDIT_LOG)
def get_audit_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        "logs": [log.to_dict() for log in logs.items],
        "total": logs.total,
        "pages": logs.pages,
        "current_page": logs.page
    })

