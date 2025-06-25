from functools import wraps
from flask import request, jsonify, g, session, current_app, redirect, Flask # Added redirect, Flask type hint
from flask_jwt_extended import get_jwt_identity # For JWT identity if needed in early middleware
import logging
import uuid
from datetime import datetime, timedelta
from functools import wraps
from flask_login import current_user, logout_user


# New imports for middleware functionality
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_compress import Compress
from werkzeug.exceptions import RequestEntityTooLarge, HTTPException, default_exceptions # For payload size error handling
import ipaddress # For IP whitelisting

# Assuming these utilities exist from previous implementations
from backend.utils.csrf_protection import CSRFProtection
from backend.utils.sanitization import InputSanitizer
from backend.models.user_models import User
# Assuming RBACService is defined elsewhere and imported, or defined below for self-containment
# from backend.services.rbac_service import RBACService


# It's good practice to get loggers this way.
logger = logging.getLogger(__name__)
security_logger = logging.getLogger('security')


# --- Global Flask Extensions Initialization ---
# These are initialized globally and then `init_app` is called within setup_middleware
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10 per minute", "200 per day"], # Global default rate limits
    storage_uri="memory://", # Use "redis://localhost:6379" or similar in production
)
compress = Compress()


# --- Middleware Definition Functions ---


def check_staff_session():
    """
    This function is now a blueprint-specific `before_request` handler.
    It checks session validity for authenticated STAFF users on admin routes.
    """
    # The path check is implicitly handled by attaching this to the admin blueprint
    if current_user.is_authenticated and current_user.is_staff:
        now = datetime.utcnow()
        timeout_reason = None

        # --- Check for maximum session lifetime (re-authentication) ---
        login_time_str = session.get('login_time')
        if login_time_str:
            login_time = datetime.fromisoformat(login_time_str)
            if now - login_time > current_app.config['SESSION_MAX_LIFETIME']:
                timeout_reason = "Session has expired for security reasons."
        else:
            # This is a fallback, login time should be set at login
            session['login_time'] = now.isoformat()

        # --- Check for inactivity timeout ---
        last_activity_str = session.get('last_activity_time')
        if last_activity_str:
            last_activity = datetime.fromisoformat(last_activity_str)
            timeout_duration = (
                current_app.config['ADMIN_INACTIVITY_TIMEOUT']
                if current_user.is_admin
                else current_app.config['STAFF_INACTIVITY_TIMEOUT']
            )
            if now - last_activity > timeout_duration:
                timeout_reason = "Session timed out due to inactivity."
        
        if timeout_reason:
            return jsonify({
                "error": "Authentication Required", 
                "message": timeout_reason,
                "reason": "reauth_required"
            }), 401

        # Update last activity time if all checks pass
        session['last_activity_time'] = now.isoformat()


            
def mfa_check_middleware(app):
    """
    Registers a 'before_request' hook to enforce Multi-Factor Authentication (MFA).
    """
    @app.before_request
    def check_mfa_status():
        protected_prefixes = ('/api/admin/', '/api/b2b/')
        exempt_endpoints = (
            'admin_api.login',
            'admin_api.verify_mfa',
            'b2b_api.login',
            'b2b_api.verify_mfa',
            'admin_auth.forgot_password',
            'admin_auth.reset_password'
        )

        is_protected_route = request.path.startswith(protected_prefixes)
        is_exempt_endpoint = request.endpoint in exempt_endpoints

        if is_protected_route and not is_exempt_endpoint:
            if current_user.is_authenticated and not session.get('mfa_authenticated'):
                security_logger.warning(
                    f"MFA bypass attempt blocked for user {current_user.id if current_user.is_authenticated else 'unauthenticated'} "
                    f"accessing endpoint {request.endpoint} from IP {request.remote_addr}",
                    extra={'request_id': getattr(g, 'request_id', 'unknown'),
                           'user_id': current_user.id if current_user.is_authenticated else None}
                )
                return jsonify({
                    "error": "MFA verification required.",
                    "mfa_required": True
                }), 403


# Placeholder for RBACService if it's not defined elsewhere
# In a real application, this would be in backend/services/rbac_service.py
class RBACService:
    @staticmethod
    def user_is_staff(user_id):
        # This is a placeholder. Implement actual logic to check if a user is staff.
        # This might involve querying the database or checking user roles.
        # For now, we'll return True for demonstration purposes if a user_id is provided.
        # You should replace this with your actual RBAC logic.
        return user_id is not None # Simple placeholder: any authenticated user is "staff" for this check


# --- Main Middleware Setup Function ---

def setup_middleware(app: Flask):
    """
    Setup global middleware for the Flask application.

    This function integrates:
    1. Global Request ID Generation & Initial Logging
    2. Suspicious Request Path Logging
    3. HTTPS Redirection
    4. Global CORS Policy
    5. Global Rate Limiting
    6. Conditional Request Payload Size Limit
    8. MFA Check Middleware
    9. Global Security Headers
    10. Global Response Finished Logging
    11. Centralized Error Handling
    12. Response Compression
    """

    # 1. Initialize Flask Extensions
    limiter.init_app(app)
    compress.init_app(app)
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000", # Vue.js development server
                "http://127.0.0.1:3000", # Another common dev address
                "https://your-frontend-domain.com", # Your production frontend domain
                # Add any other allowed origins here
            ],
            "methods": ["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization", "X-CSRF-TOKEN"],
            "supports_credentials": True # Important for JWT in HttpOnly cookies or sessions
        }
    })

    # 2. Global Request ID Generation & Initial Logging (before request)
    @app.before_request
    def log_request_started():
        g.request_id = str(uuid.uuid4())
        logger.info({
            'event': 'request_started',
            'request_id': g.request_id,
            'method': request.method,
            'path': request.path,
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown')
        })

    # 3. Suspicious Request Path Logging (before request)
    @app.before_request
    def check_suspicious_request_path():
        if any(pattern in request.path.lower() for pattern in ['script', 'eval', 'alert']):
            security_logger.warning(f"Suspicious request path: {request.path} from {request.remote_addr}",
                                    extra={'request_id': getattr(g, 'request_id', 'unknown'), 'ip': request.remote_addr})

    # 4. HTTPS Redirection Middleware (before request)
    @app.before_request
    def redirect_to_https():
        # Only redirect if not already HTTPS
        if not request.is_secure:
            # Check X-Forwarded-Proto for requests behind a proxy/load balancer
            # Assumes TLS termination at the load balancer
            if request.headers.get('X-Forwarded-Proto') == 'http':
                url = request.url.replace("http://", "https://", 1)
                security_logger.info(f"Redirecting HTTP to HTTPS: {request.url} -> {url}",
                                     extra={'request_id': getattr(g, 'request_id', 'unknown')})
                return redirect(url, code=301)
            # If not behind a proxy and not secure (e.g., local dev)
            elif not app.debug: # Only redirect if not in debug mode
                url = request.url.replace("http://", "https://", 1)
                security_logger.warning(f"Forcing HTTPS redirect directly (not behind proxy): {request.url} -> {url}",
                                        extra={'request_id': getattr(g, 'request_id', 'unknown')})
                return redirect(url, code=301)

    # 5. Conditional Request Payload Size Limit (before request)
    # This must run after basic authentication if current_user is used to determine role
    # If using JWT for role, user_id from get_jwt_identity() could be used earlier.
    # Given `current_user` in mfa_check_middleware, we assume Flask-Login is set up
    # and `current_user` is populated early enough for this.
    @app.before_request
    def check_payload_size_limit():
        MAX_SIZE_USER = 1 * 1024 * 1024  # 1 MB
        MAX_SIZE_STAFF = 25 * 1024 * 1024 # 25 MB

        # Skip GET/HEAD requests as they don't have bodies
        if request.method not in ['POST', 'PUT', 'PATCH']:
            return

        content_length = request.content_length
        if content_length is None:
            # Cannot determine content length, might be a chunked transfer
            security_logger.warning("Request without Content-Length header. Cannot apply size limit.",
                                    extra={'request_id': getattr(g, 'request_id', 'unknown')})
            return # Let the request proceed, it might be handled by web server or app logic

        limit_exceeded = False
        limit_type = "user"
        effective_limit = MAX_SIZE_USER

        if current_user.is_authenticated and RBACService.user_is_staff(current_user.id):
            effective_limit = MAX_SIZE_STAFF
            limit_type = "staff"
        else:
            effective_limit = MAX_SIZE_USER
            limit_type = "user"

        if content_length > effective_limit:
            limit_exceeded = True

        if limit_exceeded:
            security_logger.warning(
                f"Payload size limit exceeded for {limit_type} user. "
                f"User: {current_user.id if current_user.is_authenticated else 'unauthenticated'}. "
                f"Size: {content_length} bytes, Limit: {effective_limit} bytes. "
                f"Endpoint: {request.path}, IP: {request.remote_addr}",
                extra={'request_id': getattr(g, 'request_id', 'unknown'),
                       'user_id': current_user.id if current_user.is_authenticated else None}
            )
            return jsonify(status="error", message=f"Request payload too large. Max {effective_limit / (1024*1024):.0f}MB allowed for your role."), 413 # 413 Payload Too Large


    # 8. Global Security Headers (after request)
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Default CSP (can be overridden by more specific middleware for admin panel)
        # Note: 'unsafe-inline' for scripts/styles should be avoided in production if possible.
        # This mirrors your original CSP.
        default_csp = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;"
        response.headers['Content-Security-Policy'] = default_csp

        return response

    # 9. Global Response Finished Logging (after request)
    @app.after_request
    def log_request_finished(response):
        logger.info({
            'event': 'request_finished',
            'request_id': getattr(g, 'request_id', 'unknown'),
            'status_code': response.status_code,
            'content_length': response.content_length
        })
        return response

    # 10. Centralized Error Handling (global handlers)
    # These should be defined AFTER other middleware if you want
    # other middleware errors to fall into these handlers.
    for code in default_exceptions.keys():
        @app.errorhandler(code)
        def handle_http_exception(e):
            request_id = getattr(g, 'request_id', 'unknown')
            security_logger.error(f"HTTP Error {e.code}: {e.description} for {request.path}",
                                  exc_info=True, extra={'request_id': request_id, 'ip': request.remote_addr})
            response = jsonify({
                "status": "error",
                "message": getattr(e, 'description', 'An error occurred'),
                "code": e.code
            })
            return response, e.code

    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        request_id = getattr(g, 'request_id', 'unknown')
        security_logger.critical(f"Unhandled exception: {e} for {request.path}",
                                 exc_info=True, extra={'request_id': request_id, 'ip': request.remote_addr})
        response = jsonify({
            "status": "error",
            "message": "An unexpected internal server error occurred.",
            "code": 500
        })
        return response, 500

    # Note: `sanitize_request_data` (decorator for form/query args) is a route-level decorator,
    # not global middleware. It remains to be applied individually to routes if needed.


# --- Original sanitize_request_data decorator (for individual route application) ---
def sanitize_request_data(f):
    """
    Decorator to sanitize all incoming request data (JSON, form, and query args).
    This is a proactive security measure against XSS and other injection attacks.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # JSON body is now globally sanitized by `sanitize_json_request_data` middleware,
        # and request._cached_json is overwritten.

        # This part handles form data if not globally handled:
        if request.form:
            sanitized_form = {key: InputSanitizer.sanitize_string(value) for key, value in request.form.items()}
            g.sanitized_form = sanitized_form # Store in g for access

        # This part handles query arguments:
        if request.args:
            sanitized_args = {key: InputSanitizer.sanitize_string(value) for key, value in request.args.items()}
            g.sanitized_args = sanitized_args # Store in g for access

        return f(*args, **kwargs)
    return decorated_function
