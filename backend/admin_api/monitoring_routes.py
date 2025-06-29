from flask import Blueprint, jsonify, request
from backend.utils.decorators import staff_required, roles_required, permissions_required
from backend.services.monitoring_service import MonitoringService
import requests

monitoring_bp = Blueprint('monitoring_bp', __name__, url_prefix='/admin/monitoring')

@monitoring_bp.route('/health', methods=['GET'])
@roles_required ('Admin', 'Dev', 'Manager')
def get_system_health():
    """
    Get the health status of various system components.
    This could include database connectivity, external API status, etc.
    """
    try:
        health_status = MonitoringService.get_system_health()
        # If any component is not healthy, we might want to return a 503 Service Unavailable
        # For now, we return the status of all components with a 200 OK.
        is_healthy = all(status['status'] == 'ok' for status in health_status.values())
        
        return jsonify(status="success", data={"is_healthy": is_healthy, "components": health_status}), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An error occurred while checking system health."), 500

@monitoring_bp.route('/latest-errors', methods=['GET'])
@roles_required ('Admin', 'Dev', 'Manager')
def get_latest_errors():
    """
    Fetches the latest errors from the application's log file via the MonitoringService.
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        errors = MonitoringService.get_latest_errors(limit=limit)
        return jsonify(status="success", data=errors)
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Failed to serve error logs: {e}")
        return jsonify(status="error", message="An internal error occurred while fetching error logs."), 500

@monitoring_bp.route('/error-logs', methods=['GET'])
@roles_required ('Admin', 'Dev', 'Manager')
def get_error_logs():
    """
    Retrieve recent error logs from the system.
    This is a simplified endpoint; a real system would use a dedicated logging service.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)

        logs_pagination = MonitoringService.get_error_logs_paginated(page=page, per_page=per_page)
        
        return jsonify({
            "status": "success",
            "data": [log.to_dict() for log in logs_pagination.items],
            "total": logs_pagination.total,
            "pages": logs_pagination.pages,
            "current_page": logs_pagination.page
        }), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="Failed to retrieve error logs."), 500


@monitoring_bp.route('/monitoring/celery-status', methods=['GET'])
@roles_required ('Admin', 'Dev', 'Manager')
def get_celery_status():
    celery_status = MonitoringService.get_celery_worker_status()
    return jsonify(celery_status)

@monitoring_bp.route('/monitoring/recent-errors', methods=['GET'])
@roles_required ('Admin', 'Dev', 'Manager')
def get_recent_errors():
    # This is a simplified example. A real implementation would involve a proper logging setup (e.g., ELK stack)
    # and this service would query that system.
    errors = {"message": "Fetching recent errors requires a dedicated logging/monitoring system."}
    return jsonify(errors), 501 # 501 Not Implemented
