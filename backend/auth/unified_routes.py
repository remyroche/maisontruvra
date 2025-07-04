"""
Unified Authentication Routes

This module provides unified authentication endpoints for both B2B and B2C users.
All authentication flows (password, TOTP, magic link) are handled through these routes.
"""

import logging
from datetime import datetime

from flask import Blueprint, g, jsonify, redirect, request, session
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from marshmallow import ValidationError

from backend.models.user_models import User
from backend.schemas import (
    AuthMethodUpdateSchema,
    LoginSchema,
    MagicLinkRequestSchema,
    MfaVerificationSchema,
    PasswordChangeSchema,
    PasswordResetConfirmSchema,
    PasswordResetRequestSchema,
    SetupTotpSchema,
    UserRegistrationSchema,
)
from backend.services.email_service import EmailService
from backend.services.exceptions import (
    InvalidCredentialsError,
    NotFoundException,
    UnauthorizedException,
    UserAlreadyExistsError,
)
from backend.services.unified_auth_service import UnifiedAuthService
from backend.utils.decorators import api_resource_handler
from backend.utils.rate_limiter import limiter

# Create blueprint
unified_auth_bp = Blueprint("unified_auth", __name__, url_prefix="/api/auth")
security_logger = logging.getLogger("security")

# Initialize service
auth_service = UnifiedAuthService()


@unified_auth_bp.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    """
    Register a new user (B2B or B2C) with optional 2FA setup.
    """
    try:
        # Validate input
        schema = UserRegistrationSchema()
        user_data = schema.load(request.get_json())

        # Register user
        user = auth_service.register_user(user_data)

        response_data = {
            "message": "Registration successful! Please check your email to verify your account.",
            "user_id": user.id,
            "requires_email_verification": True,
        }

        # If TOTP was requested during registration, include setup data
        if user_data.get("setup_2fa") and user_data.get("two_fa_method") == "totp":
            totp_data = auth_service.setup_totp(user.id)
            response_data["totp_setup"] = {
                "secret": totp_data["secret"],
                "qr_code": totp_data["qr_code"],
            }

        return jsonify(response_data), 201

    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except UserAlreadyExistsError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        security_logger.error(f"Registration error: {str(e)}")
        return jsonify({"error": "Registration failed"}), 500


@unified_auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    """
    Authenticate user with email and password.
    Returns tokens if no 2FA required, or 2FA challenge if 2FA is enabled.
    """
    try:
        # Validate input
        schema = LoginSchema()
        credentials = schema.load(request.get_json())

        # Authenticate user
        user, requires_2fa = auth_service.authenticate_user(
            credentials["email"], credentials["password"]
        )

        if not requires_2fa:
            # No 2FA required, return tokens
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            # Send security alert for new device login (optional)
            # You can implement IP tracking logic here if needed
            # EmailService.send_security_alert_email(user, request.remote_addr)

            return jsonify(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "user_type": user.user_type.value,
                        "is_2fa_enabled": user.is_2fa_enabled,
                        "is_staff": user.is_staff,
                        "is_admin": user.is_admin,
                    },
                }
            ), 200
        else:
            # 2FA required
            # Store user ID in session for 2FA verification
            session["pending_2fa_user_id"] = user.id

            return jsonify(
                {
                    "requires_2fa": True,
                    "user_id": user.id,
                    "available_methods": {
                        "totp": user.is_totp_enabled,
                        "magic_link": user.is_magic_link_enabled,
                    },
                    "is_staff": user.is_staff,
                    "is_admin": user.is_admin,
                }
            ), 200

    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except InvalidCredentialsError as e:
        security_logger.warning(
            f"Failed login attempt for email: {credentials.get('email', 'unknown')} from IP: {request.remote_addr}"
        )
        return jsonify({"error": str(e)}), 401
    except UnauthorizedException as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        security_logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "Login failed"}), 500


@unified_auth_bp.route("/verify-2fa", methods=["POST"])
@limiter.limit("5 per minute")
def verify_2fa():
    """
    Verify 2FA token and complete login process.
    """
    try:
        # Validate input
        schema = MfaVerificationSchema()
        mfa_data = schema.load(request.get_json())

        # Verify 2FA
        success = auth_service.verify_2fa(
            mfa_data["user_id"], mfa_data["mfa_token"], mfa_data["mfa_type"]
        )

        if success:
            # Clear pending 2FA session
            session.pop("pending_2fa_user_id", None)

            # Create tokens
            access_token = create_access_token(identity=mfa_data["user_id"])
            refresh_token = create_refresh_token(identity=mfa_data["user_id"])

            # Get user data
            from backend.models.user_models import User

            user = User.query.get(mfa_data["user_id"])

            # Set MFA authenticated flag in session for staff/admin users
            if user.is_staff or user.is_admin:
                session["mfa_authenticated"] = True
                session["login_time"] = datetime.utcnow().isoformat()
                session["last_activity_time"] = datetime.utcnow().isoformat()

            # Send security alert for successful 2FA login (optional)
            # EmailService.send_security_alert_email(user, request.remote_addr)

            return jsonify(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "user_type": user.user_type.value,
                        "is_2fa_enabled": user.is_2fa_enabled,
                        "is_staff": user.is_staff,
                        "is_admin": user.is_admin,
                    },
                }
            ), 200
        else:
            return jsonify({"error": "Invalid 2FA token"}), 401

    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except (UnauthorizedException, NotFoundException) as e:
        security_logger.warning(
            f"Failed 2FA attempt for user_id: {mfa_data.get('user_id', 'unknown')} from IP: {request.remote_addr}"
        )
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        security_logger.error(f"2FA verification error: {str(e)}")
        return jsonify({"error": "2FA verification failed"}), 500


@unified_auth_bp.route("/setup-totp", methods=["POST"])
@jwt_required()
def setup_totp():
    """
    Setup TOTP for the current user.
    """
    try:
        user_id = get_jwt_identity()
        totp_data = auth_service.setup_totp(user_id)

        return jsonify(
            {
                "secret": totp_data["secret"],
                "qr_code": totp_data["qr_code"],
                "provisioning_uri": totp_data["provisioning_uri"],
            }
        ), 200

    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        security_logger.error(f"TOTP setup error: {str(e)}")
        return jsonify({"error": "TOTP setup failed"}), 500


@unified_auth_bp.route("/confirm-totp", methods=["POST"])
@jwt_required()
def confirm_totp():
    """
    Confirm TOTP setup with verification code.
    """
    try:
        # Validate input
        schema = SetupTotpSchema()
        totp_data = schema.load(request.get_json())

        user_id = get_jwt_identity()
        success = auth_service.confirm_totp_setup(user_id, totp_data["totp_code"])

        if success:
            return jsonify({"message": "TOTP setup completed successfully"}), 200
        else:
            return jsonify({"error": "Invalid TOTP code"}), 400

    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        security_logger.error(f"TOTP confirmation error: {str(e)}")
        return jsonify({"error": "TOTP confirmation failed"}), 500


@unified_auth_bp.route("/request-magic-link", methods=["POST"])
@limiter.limit("3 per minute")
def request_magic_link():
    """
    Request a magic link for authentication.
    """
    try:
        # Validate input
        schema = MagicLinkRequestSchema()
        link_data = schema.load(request.get_json())

        # Always return success to prevent user enumeration
        auth_service.request_magic_link(link_data["email"])

        return jsonify(
            {
                "message": "If your account has magic link enabled, a link has been sent to your email."
            }
        ), 200

    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except Exception as e:
        security_logger.error(f"Magic link request error: {str(e)}")
        return jsonify({"error": "Magic link request failed"}), 500


@unified_auth_bp.route("/magic-link-login/<token>")
def magic_link_login(token):
    """
    Handle magic link login.
    """
    try:
        # This would typically be handled by finding the user with the token
        # and then redirecting to the frontend with appropriate tokens
        from backend.models.user_models import User

        user = User.query.filter_by(magic_link_token=token).first()

        if user and auth_service.verify_2fa(user.id, token, "magic_link"):
            # Create tokens
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            # Redirect to frontend with tokens (or handle as needed)
            frontend_url = f"{request.host_url}account/dashboard?access_token={access_token}&refresh_token={refresh_token}"
            return redirect(frontend_url)
        else:
            return redirect(f"{request.host_url}?error=invalid_token")

    except Exception as e:
        security_logger.error(f"Magic link login error: {str(e)}")
        return redirect(f"{request.host_url}?error=server_error")


@unified_auth_bp.route("/update-auth-method", methods=["POST"])
@jwt_required()
def update_auth_method():
    """
    Update user's authentication methods (enable/disable TOTP or magic link).
    """
    try:
        # Validate input
        schema = AuthMethodUpdateSchema()
        update_data = schema.load(request.get_json())

        user_id = get_jwt_identity()
        success = auth_service.update_auth_method(
            user_id=user_id,
            action=update_data["action"],
            current_password=update_data["current_password"],
            totp_code=update_data.get("totp_code"),
            magic_link_token=update_data.get("magic_link_token"),
        )

        if success:
            return jsonify(
                {"message": "Authentication method updated successfully"}
            ), 200
        else:
            return jsonify({"error": "Failed to update authentication method"}), 400

    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except UnauthorizedException as e:
        return jsonify({"error": str(e)}), 401
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        security_logger.error(f"Auth method update error: {str(e)}")
        return jsonify({"error": "Authentication method update failed"}), 500


@unified_auth_bp.route("/verify-email/<token>")
def verify_email(token):
    """
    Verify user's email address.
    """
    try:
        success = auth_service.verify_email(token)

        if success:
            return redirect(f"{request.host_url}account/dashboard?verified=true")
        else:
            return redirect(f"{request.host_url}?error=verification_failed")

    except Exception as e:
        security_logger.error(f"Email verification error: {str(e)}")
        return redirect(f"{request.host_url}?error=verification_failed")


@unified_auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token.
    """
    try:
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id)
        return jsonify({"access_token": new_access_token}), 200
    except Exception as e:
        security_logger.error(f"Token refresh error: {str(e)}")
        return jsonify({"error": "Token refresh failed"}), 500


@unified_auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    Logout user (client-side token removal).
    """
    # Clear any server-side session data
    session.pop("mfa_authenticated", None)
    session.pop("login_time", None)
    session.pop("last_activity_time", None)
    session.pop("pending_2fa_user_id", None)

    # Log the logout action
    user_id = get_jwt_identity()
    if user_id:
        security_logger.info(f"User {user_id} logged out")

    return jsonify({"message": "Logged out successfully"}), 200


@unified_auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
@api_resource_handler(model=User, request_schema=PasswordChangeSchema, log_action=True)
def change_password():
    """
    Change user's password.
    """
    # Get validated data from the api_resource_handler
    password_data = g.validated_data

    # Get the current user
    user_id = get_jwt_identity()
    from backend.models.user_models import User

    user = User.query.get(user_id)

    if not user:
        raise NotFoundException("User not found")

    # Verify current password
    from backend.utils.encryption import check_password, hash_password

    if not check_password(password_data["current_password"], user.password_hash):
        raise UnauthorizedException("Current password is incorrect")

    # Update password
    user.password_hash = hash_password(password_data["new_password"])

    # Send confirmation email using EmailService
    EmailService.send_password_change_confirmation(user)

    # Return the user object for the api_resource_handler to handle
    return user


# Password reset endpoints (reusing existing functionality)
@unified_auth_bp.route("/request-password-reset", methods=["POST"])
@limiter.limit("5 per hour")
@api_resource_handler(
    model=User, request_schema=PasswordResetRequestSchema, log_action=True
)
def request_password_reset():
    """
    Request password reset email.
    """
    # Get validated data from the api_resource_handler
    reset_data = g.validated_data

    # Find user and send password reset email using EmailService
    from backend.utils.token_utils import generate_password_reset_token

    user = User.query.filter_by(email=reset_data["email"]).first()

    # Always return the same response regardless of whether the user exists
    # This prevents user enumeration attacks
    if not user:
        # Return a dummy user object to satisfy the api_resource_handler
        # This will be converted to the standard success message
        dummy_user = User()
        dummy_user.id = 0  # This ID will never be used
        return dummy_user

    # Generate password reset token
    token = generate_password_reset_token(user.email)

    # Send email using EmailService
    EmailService.send_password_reset_email(user, token)

    # Return the user object for the api_resource_handler to handle
    return user


@unified_auth_bp.route("/reset-password", methods=["POST"])
@limiter.limit("5 per hour")
@api_resource_handler(
    model=User, request_schema=PasswordResetConfirmSchema, log_action=True
)
def reset_password():
    """
    Reset password with token.
    """
    # Get validated data from the api_resource_handler
    reset_data = g.validated_data

    # Verify token and reset password
    from backend.utils.encryption import hash_password
    from backend.utils.token_utils import verify_password_reset_token

    try:
        # Verify the token
        email = verify_password_reset_token(reset_data["token"])
        user = User.query.filter_by(email=email).first()

        if not user:
            raise UnauthorizedException("Invalid or expired token")

        # Update password
        user.password_hash = hash_password(reset_data["new_password"])

        # Send confirmation email using EmailService
        EmailService.send_password_change_confirmation(user)

        # Return the user object for the api_resource_handler to handle
        return user

    except Exception as token_error:
        security_logger.error(f"Token verification error: {str(token_error)}")
        raise UnauthorizedException("Invalid or expired token") from token_error


# Admin routes for managing user authentication
@unified_auth_bp.route("/admin/disable-mfa/<int:user_id>", methods=["POST"])
@jwt_required()
@api_resource_handler(model=User, log_action=True, lookup_field="id")
def admin_disable_mfa(user_id):
    """
    Admin endpoint to disable MFA for a user.
    """
    # Check if the current user is an admin
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if not current_user or not current_user.is_admin:
        security_logger.warning(
            f"Non-admin user {current_user_id} attempted to disable MFA for user {user_id}"
        )
        raise UnauthorizedException("Admin privileges required")

    # Get the target user
    target_user = User.query.get(user_id)
    if not target_user:
        raise NotFoundException(f"User with ID {user_id} not found")

    # Disable MFA for the user
    auth_service.admin_disable_mfa(user_id)

    # Log the action
    security_logger.info(f"Admin {current_user_id} disabled MFA for user {user_id}")

    # Return the user object for the api_resource_handler to handle
    return target_user


@unified_auth_bp.route("/admin/trigger-password-reset/<int:user_id>", methods=["POST"])
@jwt_required()
@api_resource_handler(model=User, log_action=True, lookup_field="id")
def admin_trigger_password_reset(user_id):
    """
    Admin endpoint to trigger a password reset for a user.
    """
    # Check if the current user is an admin
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if not current_user or not current_user.is_admin:
        security_logger.warning(
            f"Non-admin user {current_user_id} attempted to trigger password reset for user {user_id}"
        )
        raise UnauthorizedException("Admin privileges required")

    # Get the target user
    target_user = User.query.get(user_id)
    if not target_user:
        raise NotFoundException(f"User with ID {user_id} not found")

    # Trigger password reset for the user
    auth_service.admin_trigger_password_reset(user_id)

    # Log the action
    security_logger.info(
        f"Admin {current_user_id} triggered password reset for user {user_id}"
    )

    # Return the user object for the api_resource_handler to handle
    return target_user
