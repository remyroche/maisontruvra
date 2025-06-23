from functools import wraps
from flask import request, jsonify, g, session
from flask_jwt_extended import get_jwt_identity, jwt_required
from backend.utils.csrf_protection import CSRFProtection
from backend.utils.sanitization import sanitize_input
import logging
import uuid

logger = logging.getLogger(__name__)
security_logger = logging.getLogger('security')

class RequestLoggingMiddleware:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def before_request(self):
        # Generate request ID for tracing
        g.request_id = str(uuid.uuid4())

        # Log incoming request
        logger.info({
            'request_id': g.request_id,
            'method': request.method,
            'path': request.path,
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown')
        })

    def after_request(self, response):
        # Log response
        logger.info({
            'request_id': getattr(g, 'request_id', 'unknown'),
            'status_code': response.status_code,
            'content_length': response.content_length
        })
        return response

def rbac_check(required_role):
    """
    Enhanced RBAC decorator with proper logging and CSRF protection.
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            if not user_id:
                security_logger.warning({
                    'message': 'Unauthenticated access attempt',
                    'endpoint': request.path,
                    'ip': request.remote_addr,
                    'request_id': getattr(g, 'request_id', 'unknown')
                })
                return jsonify({'error': 'Authentication required.'}), 401

            # Get user info (you'll need to implement this based on your User model)
            from backend.models.user_models import User
            user = User.query.get(user_id)
            if not user or not user.is_active:
                security_logger.warning({
                    'message': 'Inactive user access attempt',
                    'userId': user_id,
                    'endpoint': request.path,
                    'ip': request.remote_addr,
                    'request_id': getattr(g, 'request_id', 'unknown')
                })
                return jsonify({'error': 'Account inactive.'}), 401

            if user.role.value != required_role:
                security_logger.warning({
                    'message': 'RBAC Access Denied',
                    'userId': user_id,
                    'requiredRole': required_role,
                    'userRole': user.role.value,
                    'endpoint': request.path,
                    'ip': request.remote_addr,
                    'request_id': getattr(g, 'request_id', 'unknown')
                })
                return jsonify({'error': 'Forbidden: Insufficient permissions.'}), 403

            # Store user info in g for use in the route
            g.user = {
                'id': user.id,
                'email': user.email,
                'role': user.role.value
            }

            # Validate CSRF token for state-changing requests
            if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                try:
                    CSRFProtection.validate_csrf_token()
                except Exception as e:
                    security_logger.warning({
                        'message': 'CSRF validation failed',
                        'userId': user_id,
                        'endpoint': request.path,
                        'error': str(e),
                        'request_id': getattr(g, 'request_id', 'unknown')
                    })
                    return jsonify({'error': 'CSRF validation failed'}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_request_data(f):
    """Decorator to sanitize all incoming request data."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Sanitize JSON data
        if request.is_json and request.get_json():
            request._cached_json = sanitize_input(request.get_json())

        # Sanitize form data
        if request.form:
            sanitized_form = {}
            for key, value in request.form.items():
                sanitized_form[key] = sanitize_input(value)
            request.form = sanitized_form

        # Sanitize query parameters
        if request.args:
            sanitized_args = {}
            for key, value in request.args.items():
                sanitized_args[key] = sanitize_input(value)
            request.args = sanitized_args

        return f(*args, **kwargs)
    return decorated_function

from flask import Flask, request, g
from backend.utils.sanitization import InputSanitizer
from backend.utils.csrf_protection import CSRFProtection
import logging

security_logger = logging.getLogger('security')

def setup_middleware(app: Flask):
    """Setup middleware for the Flask application."""

    @app.before_request
    def security_headers():
        """Add security headers to all responses."""
        # Log suspicious requests
        if any(pattern in request.path.lower() for pattern in ['script', 'eval', 'alert']):
            security_logger.warning(f"Suspicious request path: {request.path} from {request.remote_addr}")

    @app.after_request
    def add_security_headers(response):
        """Add security headers to prevent common attacks."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    @app.before_request
    def sanitize_form_data():
        """Sanitize form data for security."""
        if request.method in ['POST', 'PUT', 'PATCH']:
            if request.is_json and request.json:
                g.sanitized_json = {}
                for key, value in request.json.items():
                    if isinstance(value, str):
                        g.sanitized_json[key] = InputSanitizer.sanitize_string(value)
                    else:
                        g.sanitized_json[key] = value