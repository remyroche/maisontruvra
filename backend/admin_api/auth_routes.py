from flask import Blueprint, request, jsonify
from backend.services.auth_service import AuthService
from backend.services.mfa_service import MFAService
from backend.services.exceptions import ServiceException
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token

auth_routes = Blueprint('admin_auth_routes', __name__)

@auth_routes.route('/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400

    try:
        user, is_admin = AuthService.authenticate_admin(email, password)
        if not user or not is_admin:
            return jsonify({"msg": "Invalid credentials or not an admin"}), 401

        if user.mfa_enabled:
            # If MFA is enabled, do not issue a token yet.
            # Send a response indicating that an MFA code is required.
            return jsonify({"mfa_required": True, "user_id": user.id}), 200
        
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200

    except ServiceException as e:
        return jsonify({"msg": str(e)}), 401


@auth_routes.route('/verify-mfa', methods=['POST'])
def verify_mfa():
    data = request.get_json()
    user_id = data.get('user_id')
    code = data.get('code')

    if not user_id or not code:
        return jsonify({"msg": "User ID and MFA code are required"}), 400

    try:
        if MFAService.verify_mfa_code(user_id, code):
            access_token = create_access_token(identity=user_id)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"msg": "Invalid MFA code"}), 401
    except ServiceException as e:
        return jsonify({"msg": str(e)}), 400


@auth_routes.route('/setup-mfa', methods=['POST'])
@jwt_required()
def setup_mfa():
    user_id = get_jwt_identity()
    try:
        qr_code_data_uri, secret = MFAService.setup_mfa(user_id)
        return jsonify({
            "qr_code": qr_code_data_uri,
            "secret": secret # Only for recovery, should be stored securely by the user
        }), 200
    except ServiceException as e:
        return jsonify({"msg": str(e)}), 400

@auth_routes.route('/confirm-mfa', methods=['POST'])
@jwt_required()
def confirm_mfa():
    user_id = get_jwt_identity()
    data = request.get_json()
    code = data.get('code')

    if not code:
        return jsonify({"msg": "MFA code is required"}), 400

    try:
        if MFAService.confirm_mfa_setup(user_id, code):
            return jsonify({"msg": "MFA setup confirmed and enabled."}), 200
        else:
            return jsonify({"msg": "Invalid MFA code."}), 401
    except ServiceException as e:
        return jsonify({"msg": str(e)}), 400
