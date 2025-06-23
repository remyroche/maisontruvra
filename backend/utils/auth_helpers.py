port jsonify
from flask_login import current_user
from services.email_service import EmailService

def staff_or_admin_required(f):
    """
    Decorator to ensure a user has staff or admin privileges.
    Admins are inherently considered staff.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_staff():
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

def send_password_change_email(email):
    # This is a placeholder for a more complete email service implementation
    email_service = EmailService()
    subject = "Your Password Has Been Changed"
    body = "Your password has been successfully changed. If you did not make this change, please contact support immediately."
    email_service.send_email(email, subject, body)

def send_password_reset_email(email, token):
    # This is a placeholder for a more complete email service implementation
    email_service = EmailService()
    reset_link = f"https://yourfrontend.com/reset-password?token={token}"
    subject = "Password Reset Request"
    body = f"Please use the following link to reset your password: {reset_link}"
    email_service.send_email(email, subject, body)
