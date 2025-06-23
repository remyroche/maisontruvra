
import secrets
from flask import session, request, current_app
from backend.services.exceptions import UnauthorizedException

class CSRFProtection:
    @staticmethod
    def generate_csrf_token():
        """Generate a new CSRF token."""
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(16)
        return session['csrf_token']
        
    @staticmethod
    def validate_csrf_token():
        """Validate CSRF token from request headers."""
        token = request.headers.get('X-CSRF-Token')
        if not token:
            raise UnauthorizedException("CSRF token missing")
            
        if 'csrf_token' not in session:
            raise UnauthorizedException("No CSRF token in session")
            
        if not secrets.compare_digest(token, session['csrf_token']):
            raise UnauthorizedException("Invalid CSRF token")
            
        return True

def csrf_required(f):
    """Decorator to require CSRF token validation."""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            CSRFProtection.validate_csrf_token()
        return f(*args, **kwargs)
    return decorated_function
