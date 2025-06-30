from flask import Blueprint, request, jsonify, current_user
from backend.services.user_service import UserService
from backend.services.auth_service import AuthService
from backend.utils.decorators import staff_required, roles_required, permissions_required
from backend.services.audit_log_service import AuditLogService
from backend.services.session_service import SessionService
from backend.extensions import limiter

session_routes = Blueprint('session_routes', __name__, url_prefix='/api/admin/sessions')

@session_routes.route('/sessions', methods=['GET'])
@roles_required ('Admin', 'Manager')
def list_active_sessions():
    """
    Retrieves a paginated list of all active user sessions.
    This endpoint is for administrators to monitor site-wide activity.
    [R]ead in CRUD
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    sessions_page = SessionService.get_all_active_sessions(page=page, per_page=per_page)
    
    # The response is formatted for compatibility with the frontend data table,
    # including pagination details.
    return jsonify({
        "sessions": [session.to_dict() for session in sessions_page.items],
        "total": sessions_page.total,
        "page": sessions_page.page,
        "pages": sessions_page.pages
    })

@session_routes.route('/sessions/<string:session_id>', methods=['DELETE'])
@roles_required ('Admin', 'Manager')
@limiter.limit("30 per minute") # Rate limit to prevent abuse
def terminate_session(session_id):
    """
    Terminates a specific user session (forces logout).
    This is a critical security feature for administrators.
    CRU[D] - Delete
    """
    if not session_id:
        return jsonify({"error": "Session ID is required."}), 400

    was_terminated = SessionService.terminate_session(session_id, performing_user_id=current_user.id)
    
    if was_terminated:
        # A critical security action like this must be logged.
        AuditLogService.log_action(
            user_id=current_user.id,
            action='terminate_session',
            details=f"Terminated session with ID: {session_id}."
        )
        return jsonify({"message": f"Session {session_id} has been terminated."}), 200
    else:
        return jsonify({"error": "Session not found or already inactive."}), 404


@session_routes.route('/user/<user_id>/freeze', methods=['POST'])
@roles_required ('Admin', 'Manager')
def freeze_user(user_id):
    """
    Freezes a user's account.
    ---
    tags:
      - Sessions
    parameters:
      - in: path
        name: user_id
        required: true
        schema:
          type: string
        description: The ID of the user to freeze.
    security:
      - cookieAuth: []
    responses:
      200:
        description: User account frozen successfully.
      401:
        description: Unauthorized.
      404:
        description: User not found.
    """
    if UserService.freeze_user_account(user_id):
        return jsonify({"message": "User account frozen successfully."}), 200
    return jsonify({"error": "User not found."}), 404

@session_routes.route('/user/<user_id>/unfreeze', methods=['POST'])
@roles_required ('Admin', 'Manager')
def unfreeze_user(user_id):
    """
    Unfreezes a user's account.
    ---
    tags:
      - Sessions
    parameters:
      - in: path
        name: user_id
        required: true
        schema:
          type: string
        description: The ID of the user to unfreeze.
    security:
      - cookieAuth: []
    responses:
      200:
        description: User account unfrozen successfully.
      401:
        description: Unauthorized.
      404:
        description: User not found.
    """
    if UserService.unfreeze_user_account(user_id):
        return jsonify({"message": "User account unfrozen successfully."}), 200
    return jsonify({"error": "User not found."}), 404

