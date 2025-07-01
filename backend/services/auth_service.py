
import re # Added: For regular expressions
import os # Added: For os.environ.get
from backend.models.user_models import User, UserRole
from backend.database import db
from backend.services.exceptions import ServiceError, ValidationException, UnauthorizedException, NotFoundException, InvalidPasswordException
from backend.services.mfa_service import MfaService
# generate_tokens is defined as a method in this class
from backend.services.email_service import EmailService
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature # Added: For token serialization
import logging
from flask import current_app, session, url_for
from flask_login import login_user # Added: For login_user
from ..extensions import socketio
from .monitoring_service import MonitoringService
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash
from ..services.exceptions import ValidationError
from backend.services.exceptions import UserAlreadyExistsError, InvalidCredentialsError
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from backend.utils.input_sanitizer import sanitize_input
from backend.utils.encryption import hash_password, check_password
from sqlalchemy.exc import SQLAlchemyError
from backend.database import db_session as session
from backend.models import db, User, Role, UserRole
from backend.services.email_service import EmailService
from backend.services.user_service import UserService
from backend.services.referral_service import ReferralService


# Instantiate the PasswordHasher. It's thread-safe and can be shared.
ph = PasswordHasher()


class AuthService:
    def __init__(self, logger):
        self.logger = logger
        self.email_service = EmailService(logger)
        self.user_service = UserService(logger)
        self.referral_service = ReferralService(logger)
        self.serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    def register_user(self, user_data):
        """
        Registers a new user, hashes their password, and sends a verification email.
        """
        try:
            if session.query(User).filter_by(email=user_data['email']).first():
                raise ValueError("User with this email already exists.")

            hashed_password = hash_password(user_data['password'])
            user = User(
                email=user_data['email'],
                password_hash=hashed_password,
                first_name=user_data.get('first_name'),
                last_name=user_data.get('last_name'),
                is_active=False  # User is inactive until email is verified
            )
            session.add(user)
            session.commit()

            # Assign default role
            default_role = session.query(Role).filter_by(name='user').first()
            if default_role:
                user_role = UserRole(user_id=user.id, role_id=default_role.id)
                session.add(user_role)
                session.commit()

            # Send verification email
            token = self.generate_verification_token(user.email)
            verification_url = url_for('auth.verify_email', token=token, _external=True)
            subject = "Welcome to Maison Truvra! Please Verify Your Email"
            template = "welcome_and_verify"
            context = {"user": user, "verification_url": verification_url}
            self.email_service.send_email(user.email, subject, template, context)

            self.logger.info(f"User {user.email} registered successfully. Verification email sent.")
            return user
        except (SQLAlchemyError, ValueError) as e:
            session.rollback()
            self.logger.error(f"Error during user registration: {e}")
            raise
    def authenticate_user(self, email, password):
        """
        Authenticates a user by checking their email and password.
        """
        user = self.user_service.get_user_by_email(email)
        if user and check_password(password, user.password_hash):
            if not user.is_active:
                self.logger.warning(f"Authentication attempt for inactive user: {email}")
                return None  # Or raise an exception for unverified email
            self.logger.info(f"User {email} authenticated successfully.")
            return user
        self.logger.warning(f"Failed authentication attempt for email: {email}")
        return None

    def generate_verification_token(self, email):
        """Generates a time-sensitive verification token."""
        return self.serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

    def verify_email(self, token, max_age=3600):
        """Verifies an email using the provided token."""
        try:
            email = self.serializer.loads(
                token,
                salt=current_app.config['SECURITY_PASSWORD_SALT'],
                max_age=max_age
            )
            user = self.user_service.get_user_by_email(email)
            if user:
                user.is_active = True
                user.email_verified_at = db.func.now()
                session.commit()
                self.logger.info(f"Email verified successfully for user: {email}")
                return user
            return None
        except (SignatureExpired, BadTimeSignature) as e:
            self.logger.error(f"Email verification failed: {e}")
            return None

    def change_password(self, user_id, old_password, new_password):
        """Changes a user's password after verifying the old one."""
        user = self.user_service.get_user_by_id(user_id)
        if user and check_password(old_password, user.password_hash):
            user.password_hash = hash_password(new_password)
            session.commit()
            self.logger.info(f"Password changed for user {user_id}.")
            return True
        self.logger.warning(f"Failed password change attempt for user {user_id}.")
        return False

    def send_password_reset_email(self, email):
        """Sends a password reset email to the user."""
        user = self.user_service.get_user_by_email(email)
        if user:
            token = self.generate_verification_token(email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            subject = "Password Reset Request"
            template = "password_reset_request"
            context = {"user": user, "reset_url": reset_url}
            self.email_service.send_email(email, subject, template, context)
            self.logger.info(f"Password reset email sent to {email}.")

    def reset_password(self, token, new_password):
        """Resets a user's password using a token."""
        try:
            email = self.serializer.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=3600)
            user = self.user_service.get_user_by_email(email)
            if user:
                user.password_hash = hash_password(new_password)
                session.commit()
                self.logger.info(f"Password has been reset for {email}.")
                return True
            return False
        except (SignatureExpired, BadTimeSignature):
            self.logger.error("Password reset token is invalid or has expired.")
            return False



    def get_reset_token(self, user, expires_sec=1800):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps(user.email, salt=current_app.config.get('SECURITY_PASSWORD_SALT', 'password-salt'))

    def verify_reset_token(self, token):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            email = s.loads(token, salt=current_app.config.get('SECURITY_PASSWORD_SALT', 'password-salt'), max_age=1800)
        except (SignatureExpired, BadTimeSignature):
            return None
        return User.query.filter_by(email=email).first()


        
    @staticmethod
    def verify_password(hashed_password: str, password: str) -> bool:
        """
        Verifies a user's password using Argon2.
        Returns True if the password is correct, False otherwise.
        Re-hashing logic is handled separately in the login flow.
        """
        if not hashed_password or not password:
            return False
        try:
            ph.verify(hashed_password, password)
            return True
        except VerifyMismatchError:
            # This is the expected exception for a wrong password.
            return False
        except (InvalidHash, Exception) as e:
            # Log other potential argon2 errors for debugging.
            MonitoringService.log_error(
                f"Password verification failed with an unexpected error: {e}",
                "AuthService",
                level='ERROR'
            )
            return False

    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate session token and return user data"""
        try:
            if session_token not in self.sessions:
                return None
            
            session = self.sessions[session_token]
            
            # Check if session is expired
            if datetime.now() > session["expires_at"]:
                del self.sessions[session_token]
                MonitoringService.log_security_event(
                    f"Expired session removed for user: {session.get('email', 'unknown')}",
                    "AuthService"
                )
                return None
            
            return session
            
        except Exception as e:
            MonitoringService.log_security_event(
                f"Session validation error: {str(e)}",
                "AuthService",
                level='ERROR'
            )
            return None

    def get_user_profile(self, session_token: str) -> Dict[str, Any]:
        """Get user profile data"""
        try:
            session = self.validate_session(session_token)
            if not session:
                return {"success": False, "message": "Invalid session"}
            
            user = self.db.get_user_by_id(session["user_id"])
            if not user:
                MonitoringService.log_error(
                    f"User not found for session: {session['user_id']}",
                    "AuthService"
                )
                return {"success": False, "message": "User not found"}
            
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "created_at": user.created_at,
                    "is_active": user.is_active
                }
            }
            
        except Exception as e:
            MonitoringService.log_error(
                f"Get profile error: {str(e)}",
                "AuthService",
                exc_info=True
            )
            return {"success": False, "message": "Failed to get profile"}
            
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
        """Creates a token serializer with a specific salt."""
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
            AuthService._validate_password(new_password)
            user.password_hash = ph.hash(new_password)
            db.session.commit()
            MonitoringService.log_security_event(
                f"Password reset successfully for user {user.email}",
                "AuthService"
            )
        except Exception as e:
            db.session.rollback()
            MonitoringService.log_security_event(
                f"Failed to reset password for user {user.email}: {e}",
                "AuthService",
                level='ERROR'
            )
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
    def find_user_by_email(email):
        """Finds a user by their email address."""
        user = User.query.filter_by(email=email).first()
        if not user:
            raise NotFoundException(f"User with email {email} not found.")
        return user

    def send_verification_email(self, email):
        """Generates a token and sends a verification email."""
        serializer = AuthService.get_token_serializer()
        token = serializer.dumps(email, salt='email-confirm-salt')
        EmailService.send_verification_email.delay(email, token)

    @staticmethod
    def confirm_email_verification(token, max_age=3600):
        """Verifies the email confirmation token."""
        serializer = AuthService.get_token_serializer()
        try:
            email = serializer.loads(token, salt='email-confirm-salt', max_age=max_age)
            user = User.query.filter_by(email=email).first()
            if user and not user.is_email_verified:
                user.is_email_verified = True
                db.session.commit()
            return True
        except Exception:
            return False

    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user and create session"""
        try:
            user = self.db.get_user_by_email(email)
            if not user:
                MonitoringService.log_security_event(
                    f"Login attempt with non-existent email: {email}",
                    "AuthService",
                    level='WARNING'
                )
                return {"success": False, "message": "Invalid credentials"}
            
            if not AuthService.verify_password(user.password_hash, password):
                MonitoringService.log_security_event(
                    f"Failed login attempt for: {email}",
                    "AuthService",
                    level='WARNING'
                )
                return {"success": False, "message": "Invalid credentials"}
            
            # --- Automatic Re-hashing for Security Upgrades ---
            # If verification is successful, check if the hash uses outdated parameters.
            if ph.check_needs_rehash(user.password_hash):
                try:
                    # Rehash the password with the new, more secure parameters.
                    user.password_hash = ph.hash(password)
                    db.session.commit()
                    MonitoringService.log_security_event(
                        f"Password rehashed for user {user.email}", "AuthService"
                    )
                except Exception as e:
                    db.session.rollback()
                    MonitoringService.log_error(
                        f"Failed to rehash password for user {user.email}: {e}",
                        "AuthService", level='WARNING'
                    )

            if not user.is_active:
                MonitoringService.log_security_event(
                    f"Login attempt for inactive user: {email}",
                    "AuthService",
                    level='WARNING'
                )
                return {"success": False, "message": "Account is inactive"}
            
            # Create session
            session_token = secrets.token_urlsafe(32)
            session_data = {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(hours=24)
            }
            
            self.sessions[session_token] = session_data
            MonitoringService.log_security_event(
                f"User logged in: {email}",
                "AuthService"
            )
            
            return {
                "success": True,
                "message": "Login successful",
                "session_token": session_token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            }
            
        except Exception as e:
            MonitoringService.log_security_event(
                f"Login error: {str(e)}",
                "AuthService",
                level='ERROR'
            )
            return {"success": False, "message": "Login failed"}
    
    def logout_user(self, session_token: str) -> Dict[str, Any]:
        """Logout user and invalidate session"""
        try:
            if session_token in self.sessions:
                user_email = self.sessions[session_token].get("email", "unknown")
                del self.sessions[session_token]
                MonitoringService.log_security_event(
                    f"User logged out: {user_email}",
                    "AuthService"
                )
                return {"success": True, "message": "Logout successful"}
            else:
                MonitoringService.log_security_event(
                    "Logout attempt with invalid session token",
                    "AuthService",
                    level='WARNING'
                )
                return {"success": False, "message": "Invalid session"}
                
        except Exception as e:
            MonitoringService.log_security_event(
                f"Logout error: {str(e)}",
                "AuthService",
                level='ERROR'
            )
            return {"success": False, "message": "Logout failed"}
    
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
            MonitoringService.log_security_event(
                f"MFA successful for user {user.email}",
                "AuthService"
            )
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
            MonitoringService.log_security_event(
                f"Failed MFA verification for user ID: {user_id}",
                "AuthService",
                level='WARNING'
            )
            raise UnauthorizedException("Invalid MFA token")
            
        MonitoringService.log_security_event(
            f"MFA verification successful for user ID: {user_id}",
            "AuthService"
        )
        return AuthService.generate_tokens(user.id)
        
        
    @staticmethod
    def confirm_password_reset(token, new_password):
        """Confirm password reset with token."""
        if len(new_password) < 8:
            raise ValidationException("Password must be at least 8 characters")
            
        # Verify token and update password
        # Implementation would go here
        return True
    
    @staticmethod
    def generate_tokens(user_id):
        """Generate JWT access and refresh tokens for a user"""
        try:
            from flask_jwt_extended import create_access_token, create_refresh_token
            
            # Create tokens
            access_token = create_access_token(identity=user_id)
            refresh_token = create_refresh_token(identity=user_id)
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer"
            }
            
        except Exception as e:
            MonitoringService.log_error(
                f"Error generating tokens for user {user_id}: {str(e)}",
                "AuthService",
                exc_info=True
            )
            raise ServiceError("Failed to generate authentication tokens")
