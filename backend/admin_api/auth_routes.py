from datetime import datetime
import logging

from flask import Blueprint, jsonify, request, session, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_login import current_user, login_user, logout_user
from marshmallow import ValidationError

from backend.extensions import db, limiter
from backend.services.audit_log_service import AuditLogService
from backend.services.auth_service import AuthService
from backend.services.exceptions import ServiceError
from backend.services.mfa_service import MfaService
from backend.services.user_service import UserService
from backend.utils.decorators import staff_required
from backend.utils.input_sanitizer import InputSanitizer
from backend.schemas import PasswordResetRequestSchema

admin_auth_bp = Blueprint("admin_auth_bp", __name__)
logger = logging.getLogger(__name__)
user_service = UserService(logger)
mfa_service = MfaService(logger)
auth_service = AuthService(logger)
security_logger = logging.getLogger("security")


@admin_auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """
    Endpoint for admins to request a password reset email.
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Invalid JSON data provided"}), 400

    # Validate input using marshmallow schema
    try:
        schema = PasswordResetRequestSchema()
        validated_data = schema.load(json_data)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "errors": err.messages}), 400

    try:
        # This will only succeed and send an email if the user is a valid admin
        AuthService.request_admin_password_reset(validated_data["email"])
        # Always return a success message to prevent user enumeration.
        return (
            jsonify(
                {
                    "message": "If an admin account with that email exists, a password reset link has been sent."
                }
            ),
            200,
        )
    except Exception as e:
        # Log the error, but don't expose details to the client
        current_app.logger.error(
            f"Admin password reset request failed: {e}", exc_info=True
        )
        # Still return a generic success message
        return (
            jsonify(
                {
                    "message": "If an admin account with that email exists, a password reset link has been sent."
                }
            ),
            200,
        )


@admin_auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """
    Endpoint for admins to set a new password using a valid token.
    """
    data = request.get_json()
    token = data.get("token")
    new_password = data.get("password")

    if not token or not new_password:
        return jsonify({"error": "Token and new password are required."}), 400

    # Verify the token using the specific admin salt
    user = auth_service.verify_password_reset_token(
        token, salt="admin-password-reset-salt"
    )

    if not user:
        return jsonify({"error": "Invalid or expired token."}), 401

    try:
        # Use the auth service to reset the password
        auth_service.reset_user_password(user, new_password)
        return jsonify({"message": "Password has been reset successfully."}), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status_code


@admin_auth_bp.route("/reauthenticate", methods=["POST"])
@staff_required
def reauthenticate():
    """
    Re-authenticates an existing session after a timeout.
    """
    data = request.get_json()
    password = data.get("password")

    if not auth_service.verify_password(current_user.password_hash, password):
        security_logger.warning(
            f"Re-authentication failed for user {current_user.id} due to invalid password."
        )
        return jsonify({"error": "Invalid password"}), 401

    session["login_time"] = datetime.utcnow().isoformat()
    session["last_activity_time"] = datetime.utcnow().isoformat()
    session.pop("reauth_needed", None)

    security_logger.info(f"User {current_user.id} successfully re-authenticated.")
    return jsonify({"message": "Re-authentication successful."})


@admin_auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    data = InputSanitizer.recursive_sanitize(request.get_json())
    email = data.get("email")
    password = data.get("password")

    try:
        user = auth_service.authenticate_user(email, password, is_admin=True)
        if user.two_factor_enabled:
            session["2fa_user_id"] = user.id
            return jsonify({"2fa_required": True}), 202  # Use 202 Accepted
        else:
            login_user(user)
            return jsonify({"message": "Login successful"}), 200
    except ServiceError as e:
        security_logger.warning(
            f"Failed privileged login attempt for email: {email} from IP: {request.remote_addr}"
        )
        return jsonify({"error": e.message}), e.status_code


@admin_auth_bp.route("/2fa/verify", methods=["POST"])
@limiter.limit("5 per minute")
def verify_2fa_login():
    data = InputSanitizer.recursive_sanitize(request.get_json())
    user_id = session.get("2fa_user_id")
    token = data.get("token")

    if not user_id:
        return jsonify({"error": "2FA process not initiated"}), 400

    try:
        user = mfa_service.verify_and_complete_login(user_id, token)
        login_user(user)
        session.pop("2fa_user_id", None)
        return jsonify({"message": "2FA verification successful"}), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status_code


@admin_auth_bp.route("/logout", methods=["POST"])
@staff_required
def alogout():
    logout_user()
    return jsonify({"message": "Admin or Staff logout successful"})


@admin_auth_bp.route("/check-auth", methods=["GET"])
def check_auth_status():
    if current_user.is_authenticated and (
        current_user.has_role("Admin") or current_user.has_role("Staff")
    ):
        return jsonify({"is_authenticated": True, "user": current_user.to_dict()})
    return jsonify({"is_authenticated": False})


# Setup MFA for an admin user
@admin_auth_bp.route("/mfa/setup", methods=["POST"])
@jwt_required()
@staff_required
def setup_mfa():
    """
    Initiates the MFA setup process for the currently logged-in admin user.
    Returns a secret key and a QR code for the authenticator app.
    """
    user_id = get_jwt_identity()
    try:
        secret, qr_code_data_uri = mfa_service.setup_mfa(user_id)
        return (
            jsonify(
                {
                    "status": "success",
                    "message": "MFA setup initiated. Scan the QR code with your authenticator app and verify the token.",
                    "data": {"secret": secret, "qr_code": qr_code_data_uri},
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Failed to initiate MFA setup: {e}", exc_info=True)
        return (
            jsonify(status="error", message=f"Failed to initiate MFA setup: {e}"),
            500,
        )


@admin_auth_bp.route("/auth/disable-mfa", methods=["POST"])
@staff_required
@limiter.limit("5 per hour")
def disable_mfa():
    """
    Disables MFA for the current user after password verification.
    """
    data = request.get_json()
    password = data.get("password")

    if not password:
        return jsonify({"error": "Password is required to disable MFA."}), 400

    if auth_service.verify_password(current_user.password_hash, password):
        mfa_service.disable_mfa(current_user.id)
        AuditLogService.log_action(
            user_id=current_user.id,
            action="mfa_disabled",
            details="MFA has been disabled.",
        )
        return jsonify({"message": "MFA disabled successfully."})

    return jsonify({"error": "Invalid password."}), 401


# Verify and enable MFA
@admin_auth_bp.route("/mfa/verify", methods=["POST"])
@jwt_required()
@limiter.limit("5 per minute")
def verify_mfa():
    """
    Verifies the MFA token provided by the user and enables MFA if correct.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data or "token" not in data:
        return (
            jsonify(
                status="error", message="Invalid or missing JSON body with 'token'"
            ),
            400,
        )

    token = InputSanitizer.sanitize_input(data["token"])

    try:
        if mfa_service.verify_and_enable_mfa(user_id, token):
            return (
                jsonify(
                    {
                        "status": "success",
                        "message": "MFA has been successfully enabled for your account.",
                    }
                ),
                200,
            )
        else:
            return jsonify(status="error", message="Invalid MFA token."), 400
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        logger.error(f"MFA verification error: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "An internal error occurred during MFA verification.",
                }
            ),
            500,
        )
