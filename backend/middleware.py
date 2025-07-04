import os
import time
import uuid
from datetime import datetime
from functools import wraps

from flask import Flask, current_app, g, jsonify, redirect, request, session
from flask_compress import Compress
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import current_user
from prometheus_client import Counter, Histogram
from werkzeug.exceptions import default_exceptions

from backend.loggers import app_logger as logger
from backend.loggers import security_logger
from backend.services.rbac_service import rbac_service
from backend.utils.input_sanitizer import InputSanitizer

# Prometheus metrics
REQUEST_LATENCY = Histogram(
    "request_latency_seconds", "Request latency", ["method", "endpoint"]
)
REQUEST_COUNT = Counter(
    "request_count", "Request count", ["method", "endpoint", "http_status"]
)


# --- Global Flask Extensions Initialization ---
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)
compress = Compress()


# --- Middleware Definition Functions ---


def check_staff_session(app: Flask):
    """
    Registers a blueprint-specific `before_request` handler to check session validity.
    """

    @app.before_request
    def check_staff_session_handler():
        if not request.path.startswith("/api/admin/"):
            return

        if current_user.is_authenticated and (
            rbac_service.user_is_admin(current_user.id)
            or rbac_service.user_is_staff(current_user.id)
        ):
            now = datetime.utcnow()
            timeout_reason = None

            login_time_str = session.get("login_time")
            if login_time_str:
                login_time = datetime.fromisoformat(login_time_str)
                if now - login_time > current_app.config["SESSION_MAX_LIFETIME"]:
                    timeout_reason = "Session has expired for security reasons."
            else:
                session["login_time"] = now.isoformat()

            last_activity_str = session.get("last_activity_time")
            if last_activity_str:
                last_activity = datetime.fromisoformat(last_activity_str)
                timeout_duration = (
                    current_app.config["ADMIN_INACTIVITY_TIMEOUT"]
                    if rbac_service.user_is_admin(current_user.id)
                    else current_app.config["STAFF_INACTIVITY_TIMEOUT"]
                )
                if now - last_activity > timeout_duration:
                    timeout_reason = "Session timed out due to inactivity."

            if timeout_reason:
                return (
                    jsonify(
                        {
                            "error": "Authentication Required",
                            "message": timeout_reason,
                            "reason": "reauth_required",
                        }
                    ),
                    401,
                )

            session["last_activity_time"] = now.isoformat()


def mfa_check_middleware(app: Flask):
    """
    Registers a 'before_request' hook to enforce Multi-Factor Authentication (MFA).
    """

    @app.before_request
    def check_mfa_status():
        protected_prefixes = ("/api/admin/", "/api/b2b/")
        exempt_endpoints = (
            "admin_api.login",
            "admin_api.verify_mfa",
            "b2b_api.login",
            "b2b_api.verify_mfa",
            "admin_auth.forgot_password",
            "admin_auth.reset_password",
        )

        is_protected_route = request.path.startswith(protected_prefixes)
        is_exempt_endpoint = request.endpoint in exempt_endpoints

        if is_protected_route and not is_exempt_endpoint:
            if current_user.is_authenticated and not session.get("mfa_authenticated"):
                security_logger.warning(
                    f"MFA bypass attempt blocked for user {current_user.id if current_user.is_authenticated else 'unauthenticated'} "
                    f"accessing endpoint {request.endpoint} from IP {request.remote_addr}",
                    extra={
                        "request_id": getattr(g, "request_id", "unknown"),
                        "user_id": current_user.id
                        if current_user.is_authenticated
                        else None,
                    },
                )
                return (
                    jsonify(
                        {"error": "MFA verification required.", "mfa_required": True}
                    ),
                    403,
                )


# --- Main Middleware Setup Function ---


def setup_middleware(app: Flask) -> None:
    """
    Setup global middleware for the Flask application.
    """

    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_id = str(uuid.uuid4())

    @app.after_request
    def after_request(response):
        if hasattr(g, "start_time"):
            latency = time.time() - g.start_time
            REQUEST_LATENCY.labels(request.method, request.path).observe(latency)

        REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()

        if hasattr(g, "request_id"):
            response.headers["X-Request-ID"] = g.request_id

        return response

    limiter.init_app(app)
    compress.init_app(app)

    allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(
        ","
    )
    CORS(
        app,
        resources={r"/api/*": {"origins": allowed_origins}},
        supports_credentials=True,
    )

    @app.before_request
    def log_request_started():
        logger.info(
            {
                "event": "request_started",
                "request_id": g.request_id,
                "method": request.method,
                "path": request.path,
                "ip": request.remote_addr,
            }
        )

    @app.before_request
    def check_suspicious_request_path():
        if any(
            pattern in request.path.lower() for pattern in ["script", "eval", "alert"]
        ):
            security_logger.warning(
                f"Suspicious request path: {request.path} from {request.remote_addr}",
                extra={
                    "request_id": g.request_id,
                    "ip": request.remote_addr,
                },
            )

    @app.before_request
    def redirect_to_https():
        if request.headers.get("X-Forwarded-Proto") == "http":
            url = request.url.replace("http://", "https://", 1)
            return redirect(url, code=301)

    @app.before_request
    def check_payload_size_limit():
        MAX_SIZE_USER = 1 * 1024 * 1024  # 1 MB
        MAX_SIZE_STAFF = 25 * 1024 * 1024  # 25 MB

        if request.method not in ["POST", "PUT", "PATCH"]:
            return

        content_length = request.content_length
        if content_length is None:
            return

        effective_limit = (
            MAX_SIZE_STAFF
            if current_user.is_authenticated
            and rbac_service.user_is_staff(current_user.id)
            else MAX_SIZE_USER
        )

        if content_length > effective_limit:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Request payload too large. Max {effective_limit // (1024 * 1024)}MB allowed.",
                    }
                ),
                413,
            )

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    @app.after_request
    def log_request_finished(response):
        logger.info(
            {
                "event": "request_finished",
                "request_id": g.request_id,
                "status_code": response.status_code,
            }
        )
        return response

    for code in default_exceptions:

        @app.errorhandler(code)
        def handle_http_exception(e):
            logger.error(f"HTTP Error {e.code}: {e.description}", exc_info=True)
            return jsonify(error=e.description), e.code

    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
        return jsonify(error="An unexpected internal server error occurred."), 500


def sanitize_request_data(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.form:
            g.sanitized_form = {
                key: InputSanitizer.sanitize_string(value)
                for key, value in request.form.items()
            }
        if request.args:
            g.sanitized_args = {
                key: InputSanitizer.sanitize_string(value)
                for key, value in request.args.items()
            }
        return f(*args, **kwargs)

    return decorated_function
