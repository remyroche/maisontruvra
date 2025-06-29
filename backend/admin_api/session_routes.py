from flask import Blueprint, request, jsonify
from backend.services.user_service import UserService
from backend.services.auth_service import AuthService
from backend.utils.decorators import staff_required, roles_required, permissions_required


session_routes = Blueprint('session_routes', __name__, url_prefix='/api/admin/sessions')

@session_routes.route('/', methods=['GET'])
@roles_required ('Admin', 'Manager')
def get_all_sessions():
    """
    Retrieves all user sessions.
    ---
    tags:
      - Sessions
    security:
      - cookieAuth: []
    responses:
      200:
        description: A list of all user sessions.
      401:
        description: Unauthorized.
    """
    sessions = AuthService.get_all_user_sessions()
    return jsonify(sessions), 200

@session_routes.route('/<session_id>/terminate', methods=['POST'])
@roles_required ('Admin', 'Manager')
def terminate_session(session_id):
    """
    Terminates a specific user session.
    ---
    tags:
      - Sessions
    parameters:
      - in: path
        name: session_id
        required: true
        schema:
          type: string
        description: The ID of the session to terminate.
    security:
      - cookieAuth: []
    responses:
      200:
        description: Session terminated successfully.
      401:
        description: Unauthorized.
      404:
        description: Session not found.
    """
    if AuthService.terminate_user_session(session_id):
        return jsonify({"message": "Session terminated successfully."}), 200
    return jsonify({"error": "Session not found."}), 404

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

