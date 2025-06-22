from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from backend.models.user_models import User, Role, Permission
from backend.extensions import db, bcrypt, limiter
from backend.utils.sanitization import sanitize_input


auth_routes = Blueprint('admin_auth_routes', __name__)


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5/hour")
def admin_login():
    data = sanitize_input(request.get_json())
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and user.has_role('Admin') and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200

    return jsonify({"msg": "Bad email, password, or insufficient permissions"}), 401



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
