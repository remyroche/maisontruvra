
import secrets
import hmac
import hashlib
from flask import session, request, current_app
from backend.services.exceptions import ValidationException

class CSRFProtection:
    @staticmethod
    def generate_csrf_token():
        """Generate a new CSRF token."""
        token = secrets.token_urlsafe(32)
        session['csrf_token'] = token
        return token
    
    @staticmethod
    def validate_csrf_token(token: str = None):
        """Validate CSRF token from request."""
        if not token:
            token = request.headers.get('X-CSRF-Token')
        
        if not token:
            raise ValidationException("CSRF token missing")
        
        session_token = session.get('csrf_token')
        if not session_token:
            raise ValidationException("No CSRF token in session")
        
        if not hmac.compare_digest(token, session_token):
            raise ValidationException("Invalid CSRF token")
        
        return True
    
    @staticmethod
    def csrf_protect(f):
        """Decorator to protect routes with CSRF validation."""
        from functools import wraps
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                CSRFProtection.validate_csrf_token()
            return f(*args, **kwargs)
        return decorated_function
