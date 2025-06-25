from functools import wraps
from flask import jsonify
from flask_login import current_user
from backend.services.email_service import EmailService
from backend.models.user_models import User

def staff_or_admin_required(f):
    """
    Decorator to ensure a user has staff or admin privileges.
    Admins are inherently considered staff.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_staff:
            return jsonify({'error': 'Staff or Administrator access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator to ensure a user has admin privileges.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'error': 'Administrator access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


def b2b_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_b2b:
            return jsonify({'error': 'B2B account required'}), 403
        return f(*args, **kwargs)
    return decorated_function
    
def send_password_change_email(user: User):
    """Sends a confirmation email after a password change."""
    EmailService.send_password_change_confirmation(user)


def send_password_reset_email(user: User, token: str):
    """Sends an email with a password reset link."""
    reset_link = f"https://yourfrontend.com/reset-password?token={token}"
    EmailService.send_password_reset(user, token, reset_link)

