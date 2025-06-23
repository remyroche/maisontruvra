from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from backend.auth.mfa import MfaService # Assumed service
from backend.utils.sanitization import sanitize_inputfrom flask import Blueprint, request, jsonify, session
from services.user_service import UserService
from services.mfa_service import MFAService
from flask_login import login_user, logout_user, current_user
from utils.auth_helpers import admin_required
from utils.sanitization import sanitize_input
import logging

admin_auth_bp = Blueprint('admin_auth_bp', __name__)
user_service = UserService()
mfa_service = MFAService()
security_logger = logging.getLogger('security')

@admin_auth_bp.route('/login', methods=['POST'])
def admin_login():
    data = sanitize_input(request.get_json())
    email = data.get('email')
    password = data.get('password')
    
    user = user_service.authenticate_admin(email, password)
    if user:
        if user.two_factor_enabled:
            session['2fa_user_id'] = user.id
            return jsonify({'2fa_required': True}), 200
        else:
            login_user(user)
            return jsonify({'message': 'Admin login successful'}), 200
    
    security_logger.warning(f"Failed ADMIN login attempt for email: {email} from IP: {request.remote_addr}")
    return jsonify({'error': 'Invalid credentials or not an admin'}), 401

@staff_auth_bp.route('/login', methods=['POST'])
def staff_login():
    data = sanitize_input(request.get_json())
    email = data.get('email')
    password = data.get('password')
    
    user = user_service.authenticate_staff(email, password)
    if user:
        if user.two_factor_enabled:
            session['2fa_user_id'] = user.id
            return jsonify({'2fa_required': True}), 200
        else:
            login_user(user)
            return jsonify({'message': 'Admin login successful'}), 200
    
    security_logger.warning(f"Failed STAFF login attempt for email: {email} from IP: {request.remote_addr}")
    return jsonify({'error': 'Invalid credentials or not an admin'}), 401

@admin_auth_bp.route('/2fa/verify', methods=['POST'])
def verify_2fa_login():
    data = sanitize_input(request.get_json())
    user_id = session.get('2fa_user_id')
    token = data.get('token')

    if not user_id:
        return jsonify({'error': '2FA process not initiated'}), 400

    if mfa_service.verify_2fa_login(user_id, token):
        user = user_service.get_user_by_id(user_id)
        login_user(user)
        session.pop('2fa_user_id', None)
        return jsonify({'message': '2FA verification successful'}), 200
    
    return jsonify({'error': 'Invalid 2FA token'}), 401


@admin_auth_bp.route('/logout', methods=['POST'])
@admin_required
def admin_logout():
    logout_user()
    return jsonify({'message': 'Admin logout successful'})

@admin_auth_bp.route('/check-auth', methods=['GET'])
def check_auth_status():
    if current_user.is_authenticated and current_user.is_admin():
        return jsonify({'is_authenticated': True, 'user': current_user.to_dict()})
    return jsonify({'is_authenticated': False})


# Setup MFA for an admin user
@admin_auth_bp.route('/mfa/setup', methods=['POST'])
@jwt_required()
def setup_mfa():
    """
    Initiates the MFA setup process for the currently logged-in admin user.
    Returns a secret key and a QR code for the authenticator app.
    """
    user_id = get_jwt_identity()
    try:
        # The MfaService should handle the logic of generating a new secret,
        # creating a QR code, and storing the secret temporarily.
        secret, qr_code_data_uri = MfaService.setup_mfa(user_id)
        return jsonify({
            "status": "success",
            "message": "MFA setup initiated. Scan the QR code with your authenticator app and verify the token.",
            "data": {
                "secret": secret,
                "qr_code": qr_code_data_uri
            }
        }), 200
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message=f"Failed to initiate MFA setup: {e}"), 500

# Verify and enable MFA
@admin_auth_bp.route('/mfa/verify', methods=['POST'])
@jwt_required()
def verify_mfa():
    """
    Verifies the MFA token provided by the user and enables MFA if correct.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data or 'token' not in data:
        return jsonify(status="error", message="Invalid or missing JSON body with 'token'"), 400
    
    token = sanitize_input(data['token'])

    try:
        # The MfaService should verify the token against the temporarily stored secret
        # and, if valid, permanently enable MFA for the user.
        if MfaService.verify_and_enable_mfa(user_id, token):
            return jsonify(status="success", message="MFA has been successfully enabled for your account."), 200
        else:
            return jsonify(status="error", message="Invalid MFA token."), 400
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred during MFA verification."), 500

# Disable MFA
@admin_auth_bp.route('/mfa/disable', methods=['POST'])
@jwt_required()
def disable_mfa():
    """
    Disables MFA for the currently logged-in user.
    Requires the current password for security.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data or 'password' not in data:
        return jsonify(status="error", message="Password is required to disable MFA"), 400

    password = data['password'] # Do not sanitize password, it's needed for verification
    
    try:
        # The MfaService should verify the user's password before disabling MFA.
        if MfaService.disable_mfa(user_id, password):
            return jsonify(status="success", message="MFA has been disabled."), 200
        else:
            # The service should return False if the password is wrong
            return jsonify(status="error", message="Incorrect password."), 403
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message=f"An error occurred while disabling MFA: {e}"), 500

