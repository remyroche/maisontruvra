from functools import wraps
from flask import request, jsonify, g, session, current_app
from flask_login import current_user
# Assuming these utilities exist from previous implementations
from ..utils.csrf_protection import CSRFProtection
from ..utils.sanitization import sanitize_input
from ..models.user_models import User
import logging
import uuid

# It's good practice to get loggers this way.
# 'security' can be configured as a separate logger for security-specific events.
logger = logging.getLogger(__name__)
security_logger = logging.getLogger('security')


def mfa_check_middleware(app):
    """
    Registers a 'before_request' hook to enforce Multi-Factor Authentication (MFA).
    This function is crucial for preventing MFA bypasses.

    How it works:
    After a user provides a correct password but before they provide an MFA token,
    their session is considered "partially authenticated". This middleware intercepts
    all incoming requests. If a partially authenticated user tries to access any
    protected page (anything other than the MFA verification page itself), this
    middleware blocks the request with a 403 Forbidden error.

    Args:
        app: The Flask application instance.
    """
    @app.before_request
    def check_mfa_status():
        # Define the API path prefixes that require full authentication.
        # Any route starting with these will be protected by this MFA check.
        protected_prefixes = ('/api/admin/', '/api/b2b/')

        # Define the specific endpoints that are EXEMPT from the MFA check.
        # This is critical, as it must allow the user to access the login
        # and MFA verification pages.
        exempt_endpoints = (
            'admin_api.login', 
            'admin_api.verify_mfa', # The endpoint that verifies the MFA token
            'b2b_api.login',
            'b2b_api.verify_mfa',
            # Password reset endpoints should also be exempt.
            'admin_auth.forgot_password',
            'admin_auth.reset_password'
        )

        # Determine if the current request is for a protected route
        is_protected_route = request.path.startswith(protected_prefixes)
        # Determine if the specific endpoint being called is on the exemption list
        is_exempt_endpoint = request.endpoint in exempt_endpoints

        # The core security check:
        if is_protected_route and not is_exempt_endpoint:
            # `current_user.is_authenticated` will be True after password validation.
            # `session.get('mfa_authenticated')` will only be True after MFA validation.
            # This 'if' block catches the user in the state between these two steps.
            if current_user.is_authenticated and not session.get('mfa_authenticated'):
                # Block the request and send a specific error message.
                # The frontend can use this to redirect the user to the MFA page.
                security_logger.warning(
                    f"MFA bypass attempt blocked for user {current_user.id} "
                    f"accessing endpoint {request.endpoint} from IP {request.remote_addr}"
                )
                return jsonify({
                    "error": "MFA verification required.",
                    "mfa_required": True
                }), 403 # 403 Forbidden is the appropriate status code.
        

class RequestLoggingMiddleware:
    """
    A middleware class to log the lifecycle of every request.
    This provides traceability for debugging and monitoring.
    """
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        # Register the before_request and after_request hooks
        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def before_request(self):
        """
        Executed before each request. Generates a unique ID for the request
        and logs its basic details.
        """
        # g is a special Flask object that is unique to each request.
        # Storing the request_id here makes it available throughout the request's lifecycle.
        g.request_id = str(uuid.uuid4())

        # Log essential request information for tracing.
        logger.info({
            'event': 'request_started',
            'request_id': g.request_id,
            'method': request.method,
            'path': request.path,
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown')
        })

    def after_request(self, response):
        """
        Executed after each request. Logs the outcome of the request.
        """
        logger.info({
            'event': 'request_finished',
            'request_id': getattr(g, 'request_id', 'unknown'),
            'status_code': response.status_code,
            'content_length': response.content_length
        })
        return response


def setup_security_headers(app):
    """
    Registers an 'after_request' hook to add security-related HTTP headers
    to every response, hardening the application against common web attacks.
    """
    @app.after_request
    def add_security_headers(response):
        # Prevents the browser from interpreting files as something other than what is declared by the content type.
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # Prevents the page from being displayed in an iframe, which can mitigate clickjacking attacks.
        response.headers['X-Frame-Options'] = 'DENY'
        # Enables the Cross-site scripting (XSS) filter built into most recent web browsers.
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # Enforces the use of HTTPS for a specified period of time.
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        # Helps prevent XSS and data injection attacks by restricting the sources of content.
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;"
        # Controls how much referrer information should be included with requests.
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

# Note: The following functions (sanitize_request_data) are decorators.
# They are not middleware in the same way as the functions above. They are designed
# to be applied manually to specific routes that require them, offering granular control.

def sanitize_request_data(f):
    """
    Decorator to sanitize all incoming request data (JSON, form, and query args).
    This is a proactive security measure against XSS and other injection attacks.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.is_json and request.get_json():
            # The `_cached_json` is an internal Flask attribute. Overwriting it is a way
            # to replace the original data with the sanitized version for the rest of the request.
            request._cached_json = (sanitize_input(request.get_json()), request._cached_json[1])
        
        # This part is more complex as request.form is immutable. A better pattern
        # is often to sanitize data within the route itself after accessing it.
        # However, this shows the intent of sanitizing form data.
        if request.form:
            sanitized_form = {key: sanitize_input(value) for key, value in request.form.items()}
            g.sanitized_form = sanitized_form

        if request.args:
            sanitized_args = {key: sanitize_input(value) for key, value in request.args.items()}
            g.sanitized_args = sanitized_args
            
        return f(*args, **kwargs)
    return decorated_function

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
