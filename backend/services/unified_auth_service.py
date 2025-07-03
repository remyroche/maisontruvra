"""
Unified Authentication Service

This service handles authentication for both B2B and B2C users with support for:
- Password-only authentication
- Password + TOTP authentication  
- Password + Magic Link authentication
- Unified registration and login flows
"""

import pyotp
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from flask import current_app, url_for

from backend.models.user_models import User
from backend.models.enums import UserType
from backend.database import db
from backend.services.email_service import EmailService
from backend.services.mfa_service import MfaService
from backend.services.exceptions import (
    ValidationException, UnauthorizedException, NotFoundException, 
    UserAlreadyExistsError, InvalidCredentialsError
)
from backend.utils.encryption import hash_password, check_password


class UnifiedAuthService:
    """Unified authentication service for both B2B and B2C users."""
    
    def __init__(self):
        self.mfa_service = MfaService()
    
    def register_user(self, user_data: Dict[str, Any]) -> User:
        """
        Register a new user (B2B or B2C) with optional 2FA setup.
        
        Args:
            user_data: Dictionary containing user registration data
            
        Returns:
            User: The newly created user object
            
        Raises:
            UserAlreadyExistsError: If user with email already exists
            ValidationException: If data validation fails
        """
        # Check if user already exists
        existing_user = User.query.filter_by(email=user_data['email']).first()
        if existing_user:
            raise UserAlreadyExistsError("User with this email already exists")
        
        # Create new user
        user = User(
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            email=user_data['email'],
            password_hash=hash_password(user_data['password']),
            user_type=UserType.B2B if user_data.get('user_type') == 'b2b' else UserType.B2C,
            is_active=False  # Requires email verification
        )
        
        # Setup 2FA if requested
        if user_data.get('setup_2fa') and user_data.get('two_fa_method'):
            method = user_data['two_fa_method']
            if method == 'totp':
                user.totp_secret = pyotp.random_base32()
                user.is_totp_enabled = True
                user.is_2fa_enabled = True
            elif method == 'magic_link':
                user.is_magic_link_enabled = True
                user.is_2fa_enabled = True
        
        db.session.add(user)
        db.session.commit()
        
        # Send verification email
        self._send_verification_email(user)
        
        # Send B2B-specific emails if it's a B2B registration
        if user.user_type == UserType.B2B:
            # Send B2B account pending email (account needs approval)
            EmailService.send_b2b_account_pending_email(user)
        
        return user
    
    def authenticate_user(self, email: str, password: str) -> Tuple[User, bool]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Tuple[User, bool]: User object and whether 2FA is required
            
        Raises:
            InvalidCredentialsError: If credentials are invalid
            UnauthorizedException: If account is not active
        """
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")
        
        if not user.is_active:
            raise UnauthorizedException("Account is not active. Please verify your email.")
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        db.session.commit()
        
        # For staff/admin users, TOTP is mandatory
        if user.is_staff or user.is_admin:
            # If TOTP is not set up, force setup
            if not user.totp_secret:
                raise UnauthorizedException("TOTP setup required for staff/admin users")
            
            # Always require 2FA for staff/admin regardless of user preferences
            return user, True
        else:
            # For regular users, check if 2FA is enabled
            requires_2fa = user.is_2fa_enabled and (user.is_totp_enabled or user.is_magic_link_enabled)
            return user, requires_2fa
    
    def verify_2fa(self, user_id: int, token: str, mfa_type: str) -> bool:
        """
        Verify 2FA token for user.
        
        Args:
            user_id: User's ID
            token: 2FA token to verify
            mfa_type: Type of 2FA ('totp' or 'magic_link')
            
        Returns:
            bool: True if verification successful
            
        Raises:
            NotFoundException: If user not found
            UnauthorizedException: If verification fails
        """
        user = User.query.get(user_id)
        if not user:
            raise NotFoundException("User not found")
        
        if mfa_type == 'totp' and user.is_totp_enabled:
            return self._verify_totp(user, token)
        elif mfa_type == 'magic_link' and user.is_magic_link_enabled:
            return self._verify_magic_link(user, token)
        else:
            raise UnauthorizedException("Invalid 2FA method")
    
    def setup_totp(self, user_id: int) -> Dict[str, str]:
        """
        Setup TOTP for user and return QR code data.
        
        Args:
            user_id: User's ID
            
        Returns:
            Dict containing secret and QR code
        """
        user = User.query.get(user_id)
        if not user:
            raise NotFoundException("User not found")
        
        # Generate new secret
        secret = pyotp.random_base32()
        user.totp_secret = secret
        
        # Generate QR code
        provisioning_uri = self.mfa_service.get_provisioning_uri(user.email, secret)
        qr_code = self.mfa_service.generate_qr_code(provisioning_uri)
        
        db.session.commit()
        
        return {
            'secret': secret,
            'qr_code': qr_code,
            'provisioning_uri': provisioning_uri
        }
    
    def confirm_totp_setup(self, user_id: int, totp_code: str) -> bool:
        """
        Confirm TOTP setup with verification code.
        
        Args:
            user_id: User's ID
            totp_code: TOTP code to verify
            
        Returns:
            bool: True if setup confirmed
        """
        user = User.query.get(user_id)
        if not user or not user.totp_secret:
            raise NotFoundException("User not found or TOTP not initialized")
        
        if self.mfa_service.verify_token(user.totp_secret, totp_code):
            user.is_totp_enabled = True
            user.is_2fa_enabled = True
            db.session.commit()
            return True
        
        return False
    
    def request_magic_link(self, email: str) -> bool:
        """
        Send magic link to user's email.
        
        Args:
            email: User's email address
            
        Returns:
            bool: True if link sent (always returns True to prevent enumeration)
        """
        user = User.query.filter_by(email=email).first()
        if user and user.is_magic_link_enabled:
            # Generate magic link token
            from backend.utils.token_utils import generate_magic_link_token
            token = generate_magic_link_token(user.id)
            user.magic_link_token = token
            user.magic_link_expires_at = datetime.utcnow() + timedelta(minutes=10)
            db.session.commit()
            
            # Send magic link email
            self._send_magic_link_email(user, token)
        
        return True  # Always return True to prevent user enumeration
    
    def update_auth_method(self, user_id: int, action: str, current_password: str, 
                          totp_code: Optional[str] = None, magic_link_token: Optional[str] = None) -> bool:
        """
        Update user's authentication methods.
        
        Args:
            user_id: User's ID
            action: Action to perform ('enable_totp', 'disable_totp', etc.)
            current_password: User's current password for verification
            totp_code: TOTP code (required when disabling TOTP)
            magic_link_token: Magic link token (required when disabling magic link)
            
        Returns:
            bool: True if update successful
        """
        user = User.query.get(user_id)
        if not user:
            raise NotFoundException("User not found")
        
        # Verify current password
        if not check_password(current_password, user.password_hash):
            raise UnauthorizedException("Invalid current password")
        
        if action == 'enable_totp':
            return self._enable_totp(user)
        elif action == 'disable_totp':
            return self._disable_totp(user, totp_code)
        elif action == 'enable_magic_link':
            return self._enable_magic_link(user)
        elif action == 'disable_magic_link':
            return self._disable_magic_link(user, magic_link_token)
        else:
            raise ValidationException("Invalid action")
    
    def _verify_totp(self, user: User, token: str) -> bool:
        """Verify TOTP token."""
        if not user.totp_secret:
            return False
        return self.mfa_service.verify_token(user.totp_secret, token)
    
    def _verify_magic_link(self, user: User, token: str) -> bool:
        """Verify magic link token."""
        if (not user.magic_link_token or 
            user.magic_link_token != token or 
            not user.magic_link_expires_at or
            datetime.utcnow() > user.magic_link_expires_at):
            return False
        
        # Clear the token after successful verification
        user.magic_link_token = None
        user.magic_link_expires_at = None
        db.session.commit()
        
        return True
    
    def _enable_totp(self, user: User) -> bool:
        """Enable TOTP for user."""
        if not user.totp_secret:
            user.totp_secret = pyotp.random_base32()
        user.is_totp_enabled = True
        user.is_2fa_enabled = True
        db.session.commit()
        
        # Send confirmation email
        EmailService.send_2fa_status_change_email(user, enabled=True)
        
        return True
    
    def _disable_totp(self, user: User, totp_code: str) -> bool:
        """Disable TOTP for user after verification."""
        if not totp_code or not self._verify_totp(user, totp_code):
            raise UnauthorizedException("Invalid TOTP code")
        
        user.is_totp_enabled = False
        user.totp_secret = None
        
        # Disable 2FA if no other methods are enabled
        if not user.is_magic_link_enabled:
            user.is_2fa_enabled = False
        
        db.session.commit()
        
        # Send confirmation email
        EmailService.send_2fa_status_change_email(user, enabled=False)
        
        return True
    
    def _enable_magic_link(self, user: User) -> bool:
        """Enable magic link for user."""
        user.is_magic_link_enabled = True
        user.is_2fa_enabled = True
        db.session.commit()
        
        # Send confirmation email
        EmailService.send_2fa_status_change_email(user, enabled=True)
        
        return True
    
    def _disable_magic_link(self, user: User, magic_link_token: str) -> bool:
        """Disable magic link for user after verification."""
        # Request a new magic link for verification
        if not magic_link_token:
            raise UnauthorizedException("Magic link token required")
        
        if not self._verify_magic_link(user, magic_link_token):
            raise UnauthorizedException("Invalid magic link token")
        
        user.is_magic_link_enabled = False
        
        # Disable 2FA if no other methods are enabled
        if not user.is_totp_enabled:
            user.is_2fa_enabled = False
        
        db.session.commit()
        
        # Send confirmation email
        EmailService.send_2fa_status_change_email(user, enabled=False)
        
        return True
    
    def _send_verification_email(self, user: User):
        """Send email verification email."""
        from backend.utils.token_utils import generate_email_verification_token
        token = generate_email_verification_token(user.email)
        
        # Use the existing EmailService method
        EmailService.send_verification_email(user, token)
    
    def _send_magic_link_email(self, user: User, token: str):
        """Send magic link email."""
        magic_link_url = url_for('unified_auth.magic_link_login', token=token, _external=True)
        
        # Use EmailService.send_email method with correct parameters
        EmailService.send_email(
            to=user.email,
            subject="Your Magic Link for Maison Truvra",
            template="magic_link_login.html",
            user=user,
            magic_link_url=magic_link_url,
            expires_minutes=10
        )
    
    def verify_email(self, token: str) -> bool:
        """
        Verify user's email address.
        
        Args:
            token: Email verification token
            
        Returns:
            bool: True if verification successful
        """
        try:
            from backend.utils.token_utils import verify_email_verification_token
            email = verify_email_verification_token(token)
            
            user = User.query.filter_by(email=email).first()
            if user:
                user.is_active = True
                user.email_verified_at = datetime.utcnow()
                db.session.commit()
                return True
                
        except Exception:
            pass
        
        return False
        
    def admin_disable_mfa(self, user_id: int) -> bool:
        """
        Disable MFA for a user by an admin.
        
        Args:
            user_id: ID of the user whose MFA should be disabled
            
        Returns:
            bool: True if MFA was successfully disabled
            
        Raises:
            NotFoundException: If user not found
        """
        user = User.query.get(user_id)
        if not user:
            raise NotFoundException("User not found")
            
        # Disable all 2FA methods
        user.is_2fa_enabled = False
        user.is_totp_enabled = False
        user.is_magic_link_enabled = False
        user.totp_secret = None
        user.magic_link_token = None
        user.magic_link_expires_at = None
        
        db.session.commit()
        
        # Send notification email to user
        EmailService.send_2fa_status_change_email(user, enabled=False, admin_triggered=True)
        
        return True
        
    def admin_trigger_password_reset(self, user_id: int) -> bool:
        """
        Trigger a password reset for a user by an admin.
        
        Args:
            user_id: ID of the user for whom to trigger password reset
            
        Returns:
            bool: True if password reset was successfully triggered
            
        Raises:
            NotFoundException: If user not found
        """
        user = User.query.filter_by(id=user_id).first()
        if not user:
            raise NotFoundException("User not found")
            
        # Generate password reset token
        from backend.utils.token_utils import generate_password_reset_token
        token = generate_password_reset_token(user.email)
        
        # Send password reset email
        EmailService.send_password_reset_email(user, token, admin_triggered=True)
        
        return True