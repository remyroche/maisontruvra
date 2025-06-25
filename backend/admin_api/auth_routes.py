from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from backend.auth.mfa import MfaService # Assumed service
from backend.utils.sanitization import sanitize_inputfrom flask import Blueprint, request, jsonify, session
from services.user_service import UserService
from services.mfa_service import MFAService
from flask_login import login_user, logout_user, current_user, login_required
from backend.auth.permissions import admin_required, staff_required, roles_required, permissions_required
from ..utils.decorators import log_admin_action
from utils.sanitization import sanitize_input
from ..services.auth_service import AuthService
from ..services.exceptions import ServiceError
import logging
from flask import Blueprint, request, jsonify, session, current_app
from flask_login import current_user, login_user, logout_user
from datetime import datetime
from backend.services.user_service import UserService
from backend.services.auth_service import AuthService
from backend.utils.decorators import admin_required, staff_required
from backend.loggers import security_logger

admin_auth_bp = Blueprint('admin_auth', __name__)


admin_auth_bp = Blueprint('admin_auth_bp', __name__)
user_service = UserService()
mfa_service = MFAService()
security_logger = logging.getLogger('security')


@admin_auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Endpoint for admins to request a password reset email.
    """
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({"error": "Email is required"}), 400
    
    try:
        # This will only succeed and send an email if the user is a valid admin
        AuthService.request_admin_password_reset(data['email'])
        # Always return a success message to prevent user enumeration.
        return jsonify({"message": "If an admin account with that email exists, a password reset link has been sent."}), 200
    except Exception as e:
        # Log the error, but don't expose details to the client
        current_app.logger.error(f"Admin password reset request failed: {e}", exc_info=True)
        # Still return a generic success message
        return jsonify({"message": "If an admin account with that email exists, a password reset link has been sent."}), 200


@admin_auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Endpoint for admins to set a new password using a valid token.
    """
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('password')

    if not token or not new_password:
        return jsonify({"error": "Token and new password are required."}), 400

    # Verify the token using the specific admin salt
    user = AuthService.verify_password_reset_token(token, salt='admin-password-reset-salt')

    if not user:
        return jsonify({"error": "Invalid or expired token."}), 401

    try:
        # A new service method would be needed for this
        # AuthService.reset_user_password(user, new_password)
        user.set_password(new_password) # Assuming User model has this method
        db.session.commit()
        return jsonify({"message": "Password has been reset successfully."}), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status_code


@admin_auth_bp.route('/reauthenticate', methods=['POST'])
@staff_required
@admin_required # Ensures a user must exist to even attempt re-auth
def reauthenticate():
    """
    Re-authenticates an existing session after a timeout.
    """
    data = request.get_json()
    password = data.get('password')
    
    if not current_user.check_password(password):
        security_logger.warning(f"Re-authentication failed for user {current_user.id} due to invalid password.")
        return jsonify({"error": "Invalid password"}), 401

    session['login_time'] = datetime.utcnow().isoformat()
    session['last_activity_time'] = datetime.utcnow().isoformat()
    session.pop('reauth_needed', None)
    
    security_logger.info(f"User {current_user.id} successfully re-authenticated.")
    return jsonify({"message": "Re-authentication successful."})


@admin_auth_bp.route('/login', methods=['POST'])
def login():
    data = sanitize_input(request.get_json())
    email = data.get('email')
    password = data.get('password')
    
    user = user_service.authenticate_staff_or_admin(email, password)
    if user:
        if user.two_factor_enabled:
            session['2fa_user_id'] = user.id
            return jsonify({'2fa_required': True}), 200
        else:
            login_user(user)
            return jsonify({'message': 'Login successful'}), 200
    
    security_logger.warning(f"Failed privileged login attempt for email: {email} from IP: {request.remote_addr}")
    return jsonify({'error': 'Invalid credentials or insufficient privileges'}), 401



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
@staff_required
def alogout():
    logout_user()
    return jsonify({'message': 'Admin or Staff logout successful'})

@admin_auth_bp.route('/check-auth', methods=['GET'])
def check_auth_status():
    if current_user.is_authenticated and current_user.is_staff():
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
