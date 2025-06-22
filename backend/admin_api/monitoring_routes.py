from flask import Blueprint, jsonify
from backend.services.monitoring_service import MonitoringService
from backend.auth.permissions import admin_required

monitoring_routes = Blueprint('monitoring_routes', __name__)

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