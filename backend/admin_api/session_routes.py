from flask import Blueprint, request, jsonify
from backend.services.session_service import SessionService
from backend.auth.permissions import admin_required, staff_required, roles_required, permissions_required
from ..utils.decorators import log_admin_action

session_management_bp = Blueprint('session_management_bp', __name__, url_prefix='/admin/sessions')

# READ all active sessions
@session_management_bp.route('/', methods=['GET'])
@log_admin_action
@roles_required ('Admin', 'Manager')
@admin_required
def get_sessions():
    """
    Get a paginated list of all active user sessions.
    This is a high-privilege action and should be audited.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        sessions_pagination = SessionService.get_all_sessions_paginated(page=page, per_page=per_page)
        
        return jsonify({
            "status": "success",
            "data": [s.to_dict() for s in sessions_pagination.items],
            "total": sessions_pagination.total,
            "pages": sessions_pagination.pages,
            "current_page": sessions_pagination.page
        }), 200
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred while fetching sessions."), 500

# DELETE a specific session (force logout)
@session_management_bp.route('/<session_id>', methods=['DELETE'])
@log_admin_action
@roles_required ('Admin', 'Manager')
@admin_required
def terminate_session(session_id):
    """
    Terminate a specific user session by its ID.
    This forces a user to log out.
    """
    try:
        if SessionService.terminate_session(session_id):
            return jsonify(status="success", message="Session terminated successfully."), 200
        else:
            return jsonify(status="error", message="Session not found or already inactive."), 404
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred while terminating the session."), 500

