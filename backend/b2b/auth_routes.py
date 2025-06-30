from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from backend.utils.auth_helpers import b2b_required # Assumed to handle B2B auth
from backend.utils.input_sanitizer import InputSanitizer
from backend.services.auth_service import AuthService # Corrected import
from backend.services.email_service import EmailService # Corrected import
from ..services.exceptions import ServiceError
from backend.database import db
from backend.models.user_models import User
from flask_login import current_user # Added: Import current_user
from datetime import datetime # Added: Import datetime
from flask import session # Added: Import session
from backend.schemas import B2BRegistrationSchema, LoginSchema, PasswordResetRequestSchema, PasswordResetConfirmSchema
# b2b_register function is defined in this file


b2b_auth_bp = Blueprint('b2b_auth_bp', __name__, url_prefix='/api/b2b/auth')

@b2b_auth_bp.route('/forgot-password', methods=['POST'])
def b2b_forgot_password():
    """Endpoint for B2B users to request a password reset email."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Invalid JSON data provided"}), 400
    
    # Validate input using marshmallow schema
    try:
        schema = PasswordResetRequestSchema()
        validated_data = schema.load(json_data)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "errors": err.messages}), 400

    AuthService.request_b2b_password_reset(validated_data['email'])
    # Always return a success message to prevent user enumeration
    return jsonify({"message": "If a B2B account with that email exists, a password reset link has been sent."}), 200

@b2b_auth_bp.route('/reset-password', methods=['POST'])
def b2b_reset_password():
    """Endpoint for B2B users to set a new password using a valid token."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Invalid JSON data provided"}), 400
    
    # Validate input using marshmallow schema
    try:
        schema = PasswordResetConfirmSchema()
        validated_data = schema.load(json_data)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "errors": err.messages}), 400
    
    token = validated_data['token']
    new_password = validated_data['new_password']

    # Verify using the specific B2B salt
    user = AuthService.verify_password_reset_token(token, salt='b2b-password-reset-salt')

    if not user or not user.is_b2b:
        return jsonify({"error": "Invalid or expired token."}), 401

    try:
        AuthService.reset_user_password(user, new_password)
        return jsonify({"message": "Password has been reset successfully."}), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status_code
        
# B2B User Registration Request
def register_b2b_user(data):
    """
    Helper function to register a B2B user.
    """
    # Implementation for B2B user registration
    # This would create a B2B user with pending status
    return data  # Placeholder return

@b2b_auth_bp.route('/register', methods=['POST'])
def b2b_register():
    """
    Submit a B2B account registration request for admin approval.
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify(status="error", message="Invalid JSON data provided"), 400
    
    # Validate input using marshmallow schema
    try:
        schema = B2BRegistrationSchema()
        validated_data = schema.load(json_data)
    except ValidationError as err:
        return jsonify(status="error", message="Validation failed", errors=err.messages), 400

    new_user = register_b2b_user(validated_data)
    EmailService.send_b2b_account_pending_email(new_user) 

    try:
        # This service creates a B2B account with a 'pending' status
        b2b_account = b2b_required.create_b2b_account_request(validated_data)
        return jsonify(
            status="success", 
            message="Your registration request has been submitted for approval.",
            data=b2b_account.to_dict()
        ), 201
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 409 # Conflict, e.g., user/company exists
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal server error occurred during registration."), 500

# B2B User Login
@b2b_auth_bp.route('/login', methods=['POST'])
def b2b_login():
    """
    Authenticate a B2B user and return JWT tokens.
    Ensures the user has the 'B2B' role and their account is 'approved'.
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify(status="error", message="Invalid JSON data provided"), 400
    
    # Validate input using marshmallow schema
    try:
        schema = LoginSchema()
        validated_data = schema.load(json_data)
    except ValidationError as err:
        return jsonify(status="error", message="Validation failed", errors=err.messages), 400

    email = validated_data['email']
    password = validated_data['password']

    try:
        # This service method should verify credentials and B2B status
        result = b2b_required.login_b2b_user(email, password)
        return jsonify(status="success", **result), 200
    except ValueError as e:
        # Handles cases like wrong password, user not found, account not approved, not a B2B user
        return jsonify(status="error", message=str(e)), 401 # Unauthorized
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal server error occurred."), 500

# Note: B2B password reset could potentially use the same flow as regular users,
# but might require its own endpoints if the logic or email templates differ.
# For now, we assume the main auth password reset flow is sufficient.
