from flask import Blueprint, request, jsonify
from backend.services.auth_service import AuthService
from backend.services.mfa_service import MfaService
from backend.services.email_service import EmailService
from backend.utils.sanitization import sanitize_input
from backend.utils.csrf_protection import csrf_required
from backend.services.exceptions import ValidationException, UnauthorizedException, NotFoundException
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies
import logging

auth_bp = Blueprint('auth', __name__)
mfa_service = MfaService()
email_service = EmailService()
security_logger = logging.getLogger('security')


# User Registration
@auth_bp.route('/register', methods=['POST'])
@csrf_required
def register():
    """
    Register a new user account.
    """
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Invalid JSON"), 400

    sanitized_data = sanitize_input(data)
    
    required_fields = ['email', 'password', 'first_name', 'last_name']
    if not all(field in sanitized_data for field in required_fields):
        return jsonify(status="error", message="Missing required fields"), 400

    try:
        # The AuthService handles user creation, password hashing, and validation
        user = AuthService.register_user(sanitized_data)
        token = AuthService.generate_email_confirmation_token(user)
        EmailService.send_verification_email(user, token)
        security_logger.info(f"New user registered: {user.email} (ID: {user.id}) from IP: {request.remote_addr}")
        
        return jsonify(status="success", message="User registered successfully.", data=user.to_dict()), 201

    except ValidationException as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        security_logger.error(f"Registration error: {str(e)}")
        return jsonify(status="error", message="An internal server error occurred."), 500

# User Login
@auth_bp.route('/login', methods=['POST'])
@csrf_required
def login():
    """
    Authenticate a user and return JWT tokens.
    Handles the first step of MFA if enabled.
    """
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify(status="error", message="Email and password are required."), 400

    email = sanitize_input(data['email'])
    password = data['password'] # Do not sanitize password
    
    try:
        # AuthService returns a dictionary with tokens and MFA status
        result = AuthService.login_user(email, password)
        
        if result.get('requires_mfa'):
            return jsonify(status="success", message="MFA required", requires_mfa=True, user_id=result['user_id']), 200
        else:
            access_token = create_access_token(identity=result['user_id'])
            response = jsonify(status="success", message="Login successful.")
            set_access_cookies(response, access_token)
            return response, 200
            
    except (UnauthorizedException, ValidationException) as e:
        return jsonify(status="error", message=str(e)), 401
    except Exception as e:
        security_logger.error(f"Login error: {str(e)}")
        return jsonify(status="error", message="An internal server error occurred."), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    response = jsonify(status="success", message="Logout successful.")
    # Clear the JWT cookie
    unset_jwt_cookies(response)
    return response, 200
    
# MFA Verification
@auth_bp.route('/login/verify-mfa', methods=['POST'])
@csrf_required
def verify_mfa():
    """
    Verify the MFA token for a user who has already passed the password check.
    """
    data = request.get_json()
    if not data or 'user_id' not in data or 'mfa_token' not in data:
        return jsonify(status="error", message="user_id and mfa_token are required."), 400

    user_id = data['user_id']
    mfa_token = sanitize_input(data['mfa_token'])

    try:
        # AuthService verifies the MFA token and returns final JWTs
        tokens = AuthService.verify_mfa_login(user_id, mfa_token)
        access_token = create_access_token(identity=user_id)
        response = jsonify(status="success", message="MFA verification successful")
        set_access_cookies(response, access_token)
        return response, 200
    except (UnauthorizedException, NotFoundException, ValidationException) as e:
        return jsonify(status="error", message=str(e)), 401
    except Exception as e:
        security_logger.error(f"MFA verification error: {str(e)}")
        return jsonify(status="error", message="An internal server error occurred."), 500

# Password Reset Request
@auth_bp.route('/password/request-reset', methods=['POST'])
def request_password_reset():
    """
    Initiate a password reset request. Sends an email with a reset token.
    """
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify(status="error", message="Email is required."), 400
    
    email = sanitize_input(data['email'])

    try:
        # This service method finds the user, generates a token, and dispatches an email.
        # It should always return a success message to prevent user enumeration.
        AuthService.request_password_reset(email)
        return jsonify(status="success", message="If an account with that email exists, a password reset link has been sent."), 200
    except Exception as e:
        # Log error e but still return a generic message
        return jsonify(status="success", message="If an account with that email exists, a password reset link has been sent."), 200

# Password Reset Confirmation
@auth_bp.route('/password/confirm-reset', methods=['POST'])
def confirm_password_reset():
    """
    Reset a user's password using a valid token.
    """
    data = request.get_json()
    if not data or 'token' not in data or 'new_password' not in data:
        return jsonify(status="error", message="A token and new_password are required."), 400

    token = data['token']
    new_password = data['new_password']

    try:
        # This service method verifies the token and updates the password
        if AuthService.confirm_password_reset(token, new_password):
            return jsonify(status="success", message="Your password has been reset successfully."), 200
        else:
            return jsonify(status="error", message="Invalid or expired token."), 400
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal server error occurred."), 500
