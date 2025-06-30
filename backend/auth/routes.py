
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
)
from marshmallow import ValidationError
from ..services.auth_service import AuthService
from ..services.user_service import UserService
from backend.utils.input_sanitizer import InputSanitizer
from ..utils.rate_limiter import rate_limiter
from ..services.exceptions import ValidationException, UnauthorizedException, NotFoundException
from datetime import datetime, timezone
from flask import current_app

import redis


auth_service = AuthService()
user_schema = UserSchema()
user_registration_schema = UserRegistrationSchema()

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/auth')
security_logger = logging.getLogger('security')

@auth_bp.route('/register', methods=['POST'])
@rate_limiter(limit=5, per=300) # 5 requests per 5 minutes
def register():
    json_data = request.get_json()
    if not json_data:
        return jsonify(error="Invalid input. JSON body required."), 400
    
    try:
        validated_data = user_registration_schema.load(json_data)

    except ValidationError as err:
        # Return a structured error message from the validator.
        return jsonify(errors=err.messages), 400

    try:
        # Pass the clean, validated data to the service layer.
        user = auth_service.register_user(validated_data)
        auth_service.send_verification_email(user.email)
        
        security_logger.info(f"New user registered: {user.email} (ID: {user.id}) from IP: {request.remote_addr}")
        
        return jsonify(message="Registration successful. Please check your email to verify your account."), 201

    except ValidationException as e:
        # Catches specific service-level validation errors (e.g., email already exists)
        return jsonify(error=str(e)), 409 # 409 Conflict is often better for "already exists" errors
        
    except Exception as e:
        # Catches unexpected errors during the registration process.
        security_logger.error(f"Registration error for email {validated_data.get('email')}: {str(e)}")
        return jsonify(error="An internal server error occurred."), 500
@auth_bp.route('/login', methods=['POST'])
@rate_limiter(limit=10, per=60) # 10 requests per minute
def login():
    """Authenticates a user, handling the first step of MFA if enabled."""
    data = InputSanitizer.sanitize_input(request.get_json())
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify(error="Email and password are required."), 400

    try:
        result = AuthService.login_user(email, password)
        
        if result.get('requires_mfa'):
            return jsonify(requires_mfa=True, user_id=result['user_id']), 200
        else:
            access_token = create_access_token(identity=result['user_id'])
            refresh_token = create_refresh_token(identity=result['user_id'])
            return jsonify(access_token=access_token, refresh_token=refresh_token), 200
            
    except UnauthorizedException as e:
        security_logger.warning(f"Failed login attempt for email: {email} from IP: {request.remote_addr}")
        return jsonify(error=str(e)), 401
    except Exception as e:
        security_logger.error(f"Login error for {email}: {str(e)}")
        return jsonify(error="An internal server error occurred."), 500

@auth_bp.route('/login/verify-mfa', methods=['POST'])
@rate_limiter(limit=5, per=60) # 5 requests per minute
def verify_mfa():
    """Verifies the MFA token and returns JWTs upon success."""
    data = InputSanitizer.sanitize_input(request.get_json())
    user_id = data.get('user_id')
    mfa_token = data.get('mfa_token')

    if not user_id or not mfa_token:
        return jsonify(error="user_id and mfa_token are required."), 400

    try:
        if AuthService.verify_mfa_login(user_id, mfa_token):
            access_token = create_access_token(identity=user_id)
            refresh_token = create_refresh_token(identity=user_id)
            return jsonify(access_token=access_token, refresh_token=refresh_token), 200
        else:
             raise UnauthorizedException("Invalid MFA token.")
    except (UnauthorizedException, NotFoundException) as e:
        security_logger.warning(f"Failed MFA attempt for user_id: {user_id} from IP: {request.remote_addr}")
        return jsonify(error=str(e)), 401
    except Exception as e:
        security_logger.error(f"MFA verification error: {str(e)}")
        return jsonify(error="An internal server error occurred."), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Revokes the current user's access token by adding its JTI to the blocklist.
    """
    try:
        token_data = get_jwt()
        jti = get_jwt()['jti']
        token_type = token_data["type"]
        
        # Get the expiration timestamp and calculate the remaining time in seconds
        token_exp = get_jwt()['exp']
        expires = datetime.fromtimestamp(token_exp, tz=timezone.utc)

        # Add the JTI to the Redis blocklist with an expiration
        redis_client = redis.from_url(current_app.config['REDIS_URL'])
        redis_client.set(f"jti_blocklist:{jti}", "", ex=expires - datetime.now(timezone.utc))
        
        security_logger.info(f"User {get_jwt_identity()} logged out. Revoked {token_type} token {jti}.")
        return jsonify(message=f"{token_type.capitalize()} token successfully revoked"), 200
    except Exception as e:
        security_logger.error(f"Error during logout: {str(e)}")
        return jsonify(error="An internal error occurred during logout."), 500

@auth_bp.route('/status', methods=['GET'])
@jwt_required(optional=True)
def status():
    """Checks the authentication status of the user."""
    current_user_id = get_jwt_identity()
    if current_user_id:
        user = UserService.get_user_by_id(current_user_id)
        if user:
            return jsonify(is_logged_in=True, user=user.to_dict())
    return jsonify(is_logged_in=False)

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refreshes an access token."""
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify(access_token=new_access_token)

@auth_bp.route('/password/request-reset', methods=['POST'])
@rate_limiter(limit=3, per=300) # 3 requests per 5 minutes
def request_password_reset():
    """Initiates the password reset process."""
    data = InputSanitizer.sanitize_input(request.get_json())
    email = data.get('email')
    AuthService.send_password_reset_email(email)
    # Always return a generic success message to prevent email enumeration
    return jsonify(message="If an account with that email exists, a password reset link has been sent."), 200

@auth_bp.route('/password/confirm-reset', methods=['POST'])
@rate_limiter(limit=5, per=600) # 5 requests per 10 minutes
def confirm_password_reset():
    """Resets the user's password using a valid token."""
    data = InputSanitizer.sanitize_input(request.get_json())
    token = data.get('token')
    new_password = data.get('new_password')
    
    if not token or not new_password:
        return jsonify(error="Token and new_password are required."), 400

    if AuthService.reset_password_with_token(token, new_password):
        return jsonify(message="Password has been reset successfully."), 200
    return jsonify(error="Invalid or expired token."), 400
