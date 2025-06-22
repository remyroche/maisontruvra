from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from backend.auth.permissions import permission_required, Permission
import datetime

monitoring_bp = Blueprint('monitoring_bp', __name__, url_prefix='/monitoring')

@monitoring_bp.route('/health', methods=['GET'])
@jwt_required()
@permission_required(Permission.VIEW_MONITORING)
def health_check():
    """A simple health check endpoint."""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.datetime.utcnow().isoformat()
    })


@monitoring_routes.route('/monitoring/system-health', methods=['GET'])
@admin_required
def get_system_health():
    health_status = MonitoringService.get_system_health()
    return jsonify(health_status)

@monitoring_routes.route('/monitoring/celery-status', methods=['GET'])
@admin_required
def get_celery_status():
    celery_status = MonitoringService.get_celery_worker_status()
    return jsonify(celery_status)

@monitoring_routes.route('/monitoring/recent-errors', methods=['GET'])
@admin_required
def get_recent_errors():
    # This is a simplified example. A real implementation would involve a proper logging setup (e.g., ELK stack)
    # and this service would query that system.
    errors = {"message": "Fetching recent errors requires a dedicated logging/monitoring system."}
    return jsonify(errors), 501 # 501 Not Implemented
