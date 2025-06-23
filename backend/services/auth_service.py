
from werkzeug.security import check_password_hash, generate_password_hash
from backend.models.user_models import User, UserRole
from backend.database import db
from backend.services.exceptions import ValidationException, UnauthorizedException, NotFoundException
from backend.services.mfa_service import MfaService
from backend.utils.auth_helpers import generate_tokens
import logging
from flask import current_app

logger = logging.getLogger(__name__)
security_logger = logging.getLogger('security')

class AuthService:
    @staticmethod
    def register_user(user_data):
        """Register a new user with validation."""
        email = user_data.get('email', '').strip().lower()
        password = user_data.get('password', '')
        first_name = user_data.get('first_name', '').strip()
        last_name = user_data.get('last_name', '').strip()
        
        # Validation
        if not email or '@' not in email:
            raise ValidationException("Valid email is required")
        if len(password) < 8:
            raise ValidationException("Password must be at least 8 characters")
        if not first_name or not last_name:
            raise ValidationException("First and last name are required")
            
        # Check if user exists
        if User.query.filter_by(email=email).first():
            raise ValidationException("User with this email already exists")
            
        # Create user
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=UserRole.CUSTOMER,
            is_active=True,
            email_verified=False
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        security_logger.info(f"New user registered: {email} (ID: {user.id})")
        return user
        
    @staticmethod
    def login_user(email, password):
        """Authenticate user login."""
        email = email.strip().lower()
        
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            security_logger.warning(f"Failed login attempt for email: {email}")
            raise UnauthorizedException("Invalid email or password")
            
        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")
            
        security_logger.info(f"User logged in: {email} (ID: {user.id})")
        
        # Check if MFA is enabled
        if user.totp_secret:
            return {"requires_mfa": True, "user_id": user.id}
        else:
            tokens = generate_tokens(user.id)
            return {"requires_mfa": False, **tokens}
            
    @staticmethod
    def verify_mfa_login(user_id, mfa_token):
        """Verify MFA token and complete login."""
        user = User.query.get(user_id)
        if not user:
            raise NotFoundException("User not found")
            
        if not user.totp_secret:
            raise ValidationException("MFA not enabled for this user")
            
        if not MfaService.verify_token(user.totp_secret, mfa_token):
            security_logger.warning(f"Failed MFA verification for user ID: {user_id}")
            raise UnauthorizedException("Invalid MFA token")
            
        security_logger.info(f"MFA verification successful for user ID: {user_id}")
        return generate_tokens(user.id)
        
    @staticmethod
    def request_password_reset(email):
        """Request password reset."""
        email = email.strip().lower()
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token and send email
            # Implementation would go here
            security_logger.info(f"Password reset requested for: {email}")
        
        # Always return success to prevent user enumeration
        
    @staticmethod
    def confirm_password_reset(token, new_password):
        """Confirm password reset with token."""
        if len(new_password) < 8:
            raise ValidationException("Password must be at least 8 characters")
            
        # Verify token and update password
        # Implementation would go here
        return True
