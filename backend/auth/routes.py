from flask import Blueprint, request, jsonify
from backend.services.auth_service import AuthService
from backend.services.user_service import UserService
from backend.services.exceptions import ServiceException, NotFoundException
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('public_auth_routes', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new B2C user.
    """
    data = request.get_json()
    try:
        user = UserService.create_user(data)
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token, user=user.to_dict()), 201
    except ServiceException as e:
        return jsonify({"msg": str(e)}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate a B2C user and return an access token.
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400
    
    try:
        user = AuthService.authenticate_user(email, password)
        if user:
            access_token = create_access_token(identity=user.id)
            return jsonify(access_token=access_token, user=user.to_dict()), 200
        return jsonify({"msg": "Invalid credentials"}), 401
    except ServiceException as e:
        return jsonify({"msg": str(e)}), 401

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Endpoint to handle user logout.
    In a token-based system, the client is responsible for discarding the token.
    This endpoint can be used for logging or to manage a token blocklist if implemented.
    """
    # For a simple implementation, we just confirm the action.
    # For a more advanced setup, you could add the token's jti to a blocklist.
    return jsonify({"msg": "Successfully logged out"}), 200

@auth_bp.route('/reset-password-request', methods=['POST'])
def reset_password_request():
    data = request.get_json()
    email = data.get('email')
    try:
        AuthService.send_password_reset_email(email)
        return jsonify({"msg": "If an account with that email exists, a password reset link has been sent."}), 200
    except NotFoundException:
         # Still return a success message to prevent user enumeration
        return jsonify({"msg": "If an account with that email exists, a password reset link has been sent."}), 200
    except ServiceException as e:
        return jsonify({"msg": str(e)}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    try:
        AuthService.reset_password_with_token(token, new_password)
        return jsonify({"msg": "Password has been updated successfully."}), 200
    except ServiceException as e:
        return jsonify({"msg": str(e)}), 400