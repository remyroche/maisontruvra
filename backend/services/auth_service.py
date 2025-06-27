
import re # Added: For regular expressions
import os # Added: For os.environ.get
from werkzeug.security import check_password_hash, generate_password_hash
from backend.models.user_models import User, UserRole
from backend.database import db
from backend.services.exceptions import ServiceError, ValidationException, UnauthorizedException, NotFoundException, InvalidPasswordException
from backend.services.mfa_service import MfaService
from backend.utils.auth_helpers import generate_tokens
from backend.services.email_service import EmailService # Added: For EmailService
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature # Added: For token serialization
import logging
from flask import current_app, session # Added: For session
from flask_login import login_user # Added: For login_user
from ..extensions import socketio

logger = logging.getLogger(__name__)
security_logger = logging.getLogger('security')


class AuthService:

    @staticmethod
    def _validate_password(password):
        """
        Validates a password against the policy defined in the config.
        Raises InvalidPasswordException if the policy is not met.
        """
        errors = []
        if len(password) < current_app.config.get('PASSWORD_MIN_LENGTH', 8):
            errors.append(f"Password must be at least {current_app.config['PASSWORD_MIN_LENGTH']} characters long.")
        if current_app.config.get('PASSWORD_REQUIRE_LOWERCASE') and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter.")
        if current_app.config.get('PASSWORD_REQUIRE_UPPERCASE') and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter.")
        if current_app.config.get('PASSWORD_REQUIRE_DIGIT') and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit.")
        if current_app.config.get('PASSWORD_REQUIRE_SPECIAL') and not re.search(r'[\W_]', password):
            errors.append("Password must contain at least one special character.")
    
        if errors:
            # We join errors into a single string for the exception message.
            raise InvalidPasswordException("Password validation failed: " + " ".join(errors))
    
    @staticmethod
    def get_token_serializer(salt='default'):
        """Creates a token serializer with a specific salt.""" # Corrected: URLSafeTimedSerializer was not defined
        return URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt=salt)

    @staticmethod
    def request_password_reset(email):
        user = User.query.filter_by(email=email).first()
        if user:
            # Standard token for B2C users
            ts = AuthService.get_token_serializer(salt='password-reset-salt')
            token = ts.dumps(user.email)
            reset_url = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password/{token}"
            EmailService.send_password_reset_email(user, reset_url)

    @staticmethod
    def request_admin_password_reset(email):
        """
        Handles a password reset request specifically for an admin user.
        """
        user = User.query.filter_by(email=email).first()
        # CRITICAL: Verify the user is an administrator before proceeding
        if user and user.is_admin:
            # Use a DIFFERENT salt for admin resets for enhanced security
            ts = AuthService.get_token_serializer(salt='admin-password-reset-salt')
            token = ts.dumps(user.email)
            
            # This URL should point to the admin password reset page, not the B2C one.
            reset_url = f"{os.environ.get('ADMIN_URL', 'http://localhost:8080')}/admin_reset_password.html?token={token}"
            
            # A dedicated email template should be used
            EmailService.send_admin_password_reset_email(user, reset_url)
        # Note: We don't confirm if the email exists to prevent user enumeration.

    @staticmethod
    def request_b2b_password_reset(email):
        """
        Handles a password reset request specifically for a B2B user.
        """
        user = User.query.filter_by(email=email).first()
        # CRITICAL: Verify the user is a B2B user
        if user and user.is_b2b:
            ts = AuthService.get_token_serializer(salt='b2b-password-reset-salt')
            token = ts.dumps(user.email)
            
            # This URL points to the Vue B2B portal reset page
            reset_url = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/pro/reset-password/{token}"
            
            # You might want a specific B2B email template here
            EmailService.send_password_reset_email(user, reset_url)

    @staticmethod
    def reset_user_password(user, new_password):
        """Sets a new password for a user."""
        if not user or not new_password:
            raise ServiceError("User and new password are required.")
        try:
            _validate_password(new_password)
            user.set_password(new_password)
            db.session.commit()
            current_app.logger.info(f"Password reset successfully for user {user.email}")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to reset password for user {user.email}: {e}", exc_info=True)
            raise ServiceError("Could not update password.")
            
    @staticmethod
    def verify_password_reset_token(token, salt='password-reset-salt'):
        ts = AuthService.get_token_serializer(salt=salt)
        try:
            email = ts.loads(token, max_age=3600)  # Token is valid for 1 hour
            return User.query.filter_by(email=email).first()
        except (SignatureExpired, BadTimeSignature):
            return None

    @staticmethod
    def register_user(data):
        """Registers a new user, enforcing password policy."""
        email = data.get('email')
        password = data.get('password')

        if User.query.filter_by(email=email).first():
            raise ValidationException("An account with this email already exists.")
            
        AuthService._validate_password(password)

        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        db.session.add(user)
        db.session.commit()
        socketio.emit('new_user', user.to_admin_dict(), namespace='/admin')
        AuthService.send_verification_email(user.email)
        return user

    @staticmethod
    def send_verification_email(email):
        """Generates a token and sends a verification email."""
        serializer = AuthService._get_serializer()
        token = serializer.dumps(email, salt='email-confirm-salt')
        EmailService.send_verification_email.delay(email, token)

    @staticmethod
    def confirm_email_verification(token, max_age=3600):
        """Verifies the email confirmation token."""
        serializer = AuthService._get_serializer()
        try:
            email = serializer.loads(token, salt='email-confirm-salt', max_age=max_age)
            user = User.query.filter_by(email=email).first()
            if user and not user.is_email_verified:
                user.is_email_verified = True
                db.session.commit()
            return True
        except Exception:
            return False
        
    @staticmethod
    def login(email, password, is_b2b=False, is_admin=False):
        """
        Handles the first step of logging in for any user type, with enhanced
        security checks and logging.
        """
        # Sanitize email input
        email = email.strip().lower()
        
        user = User.query.filter_by(email=email).first()

        if not user.is_email_verified:
            raise UnauthorizedException("Email not verified. Please check your inbox.")

        # Check for user existence and correct password
        if not user or not user.check_password(password):
            current_app.logger.warning(f"Failed login attempt for email: {email}")
            raise ServiceError("Invalid email or password.", 401)
            
        # Check if the user's account is active
        if not user.is_active:
            current_app.logger.warning(f"Login attempt for deactivated account: {email}")
            raise ServiceError("This account has been deactivated.", 403)

        # Verify the user has the correct role for the login portal (admin, b2b, etc.)
        if (is_b2b != user.is_b2b) or (is_admin != user.is_admin):
            current_app.logger.warning(f"Role mismatch during login attempt for email: {email}")
            raise ServiceError("Invalid credentials for this portal.", 401)

        # If MFA is not enabled for this user, log them in completely.
        if not user.two_factor_enabled:
            login_user(user) # Corrected: login_user was not defined
            session['mfa_authenticated'] = True  # Mark session as fully authenticated
            current_app.logger.info(f"User {email} logged in successfully (MFA not enabled).")
            return {'mfa_required': False, 'user': user.to_dict()}

        # --- MFA is required: Create a partial session ---
        # Store the user's ID and mark the session as pending MFA verification.
        session['mfa_pending_user_id'] = user.id
        session['mfa_authenticated'] = False
        
        # Do NOT call login_user() here. The user is not fully logged in.
        current_app.logger.info(f"MFA is required for user {email}. Awaiting verification.")
        return {'mfa_required': True}

    @staticmethod
    def verify_and_complete_login(mfa_token):
        """
        Verifies the MFA token for a user with a pending session.
        If successful, it "upgrades" the session to be fully authenticated.
        """
        user_id = session.get('mfa_pending_user_id')
        if not user_id:
            raise ServiceError("No MFA login attempt is pending.", 401)

        user = User.query.get(user_id)
        if not user:
            raise ServiceError("User not found.", 401)
        
        # Verify the token against the user's secret
        if MfaService.verify_token(user.two_factor_secret, mfa_token): # Corrected attribute name
            # Success! Now we can fully log the user in. # Corrected: login_user was not defined
            login_user(user)
            session['mfa_authenticated'] = True
            session.pop('mfa_pending_user_id', None) # Clean up the pending key
            current_app.logger.info(f"MFA successful for user {user.email}")
            return user

        # If verification fails
        raise ServiceError("Invalid MFA token.", 401)
    

            
    @staticmethod
    def verify_mfa_login(user_id, mfa_token):
        """Verify MFA token and complete login."""
        user = User.query.get(user_id)
        if not user:
            raise NotFoundException("User not found")
            
        if not user.two_factor_secret: # Corrected attribute name
            raise ValidationException("MFA not enabled for this user")
            
        if not MfaService.verify_token(user.two_factor_secret, mfa_token): # Corrected attribute name
            security_logger.warning(f"Failed MFA verification for user ID: {user_id}")
            raise UnauthorizedException("Invalid MFA token")
            
        security_logger.info(f"MFA verification successful for user ID: {user_id}")
        return generate_tokens(user.id)
        
        
    @staticmethod
    def confirm_password_reset(token, new_password):
        """Confirm password reset with token."""
        if len(new_password) < 8:
            raise ValidationException("Password must be at least 8 characters")
            
        # Verify token and update password
        # Implementation would go here
        return True
