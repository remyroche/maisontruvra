
import re # Added: For regular expressions
import os # Added: For os.environ.get
from werkzeug.security import check_password_hash, generate_password_hash
from backend.models.user_models import User, UserRole
from backend.database import db, Database
from backend.services.exceptions import ServiceError, ValidationException, UnauthorizedException, NotFoundException, InvalidPasswordException
from backend.services.mfa_service import MfaService
# generate_tokens is defined as a method in this class
from backend.services.email_service import EmailService # Added: For EmailService
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature # Added: For token serialization
import logging
from flask import current_app, session # Added: For session
from flask_login import login_user # Added: For login_user
from ..extensions import socketio
from .monitoring_service import MonitoringService
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any




class AuthService:
    def __init__(self):
        self.db = Database()
        self.sessions = {}  # In production, use Redis or similar

    def hash_password(self, password: str) -> str:
        """Hash a password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            salt, password_hash = hashed_password.split(':')
            test_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return test_hash == password_hash
        except ValueError:
            current_app.logger.error("Invalid password hash format")
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
                current_app.logger.info(f"Expired session removed for user: {session.get('email', 'unknown')}")
                return None
            
            return session
            
        except Exception as e:
            current_app.logger.error(f"Session validation error: {str(e)}")
            return None

    def get_user_profile(self, session_token: str) -> Dict[str, Any]:
        """Get user profile data"""
        try:
            session = self.validate_session(session_token)
            if not session:
                return {"success": False, "message": "Invalid session"}
            
            user = self.db.get_user_by_id(session["user_id"])
            if not user:
                current_app.logger.error(f"User not found for session: {session['user_id']}")
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
            current_app.logger.error(f"Get profile error: {str(e)}")
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

    def register_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = self.db.get_user_by_email(email)
            if existing_user:
                current_app.logger.warning(f"Registration attempt with existing email: {email}")
                return {"success": False, "message": "User already exists"}
            
            # Hash password
            hashed_password = self.hash_password(password)
            
            # Create user
            user_data = {
                "username": username,
                "email": email,
                "password_hash": hashed_password,
                "created_at": datetime.now().isoformat(),
                "is_active": True
            }
            
            user_id = self.db.create_user(user_data)
            current_app.logger.info(f"New user registered: {username} ({email})")
            
            return {
                "success": True, 
                "message": "User registered successfully",
                "user_id": user_id
            }
            
        except Exception as e:
            current_app.logger.error(f"Registration error: {str(e)}")
            return {"success": False, "message": "Registration failed"}
    
        
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
                current_app.logger.warning(f"Login attempt with non-existent email: {email}")
                return {"success": False, "message": "Invalid credentials"}
            
            if not self.verify_password(password, user.password_hash):
                current_app.logger.warning(f"Failed login attempt for: {email}")
                return {"success": False, "message": "Invalid credentials"}
            
            if not user.is_active:
                current_app.logger.warning(f"Login attempt for inactive user: {email}")
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
            current_app.logger.info(f"User logged in: {email}")
            
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
            current_app.logger.error(f"Login error: {str(e)}")
            return {"success": False, "message": "Login failed"}
    
    def logout_user(self, session_token: str) -> Dict[str, Any]:
        """Logout user and invalidate session"""
        try:
            if session_token in self.sessions:
                user_email = self.sessions[session_token].get("email", "unknown")
                del self.sessions[session_token]
                current_app.logger.info(f"User logged out: {user_email}")
                return {"success": True, "message": "Logout successful"}
            else:
                current_app.logger.warning("Logout attempt with invalid session token")
                return {"success": False, "message": "Invalid session"}
                
        except Exception as e:
            current_app.logger.error(f"Logout error: {str(e)}")
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
            current_app.logger.warning(f"Failed MFA verification for user ID: {user_id}")
            raise UnauthorizedException("Invalid MFA token")
            
        current_app.logger.info(f"MFA verification successful for user ID: {user_id}")
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
            current_app.logger.error(f"Error generating tokens for user {user_id}: {str(e)}")
            raise ServiceError("Failed to generate authentication tokens")
