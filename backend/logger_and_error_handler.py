"""
This module sets up robust, application-wide logging and centralized error handling.
It ensures all error responses are consistent, secure, and well-documented.
"""

import logging
import logging.handlers
from flask import jsonify, Blueprint, current_app, request
from werkzeug.exceptions import HTTPException
from marshmallow import ValidationError

# Import all custom exceptions from the service layer
from ..services.exceptions import (
    NotFoundException,
    ValidationException,
    AuthorizationException,
)

# Create a Blueprint for error handlers to make them modular
error_handler_bp = Blueprint("error_handlers", __name__)


class JsonFormatter(logging.Formatter):
    """Formats log records as JSON for easier parsing by log management systems."""

    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_entry["exc_info"] = self.formatException(record.exc_info)
        return str(log_entry)


def setup_logging(app):
    """
    Configures structured, rotating file-based logging.
    In a production environment, you would likely replace the file handler
    with a service like Sentry, Datadog, or AWS CloudWatch.
    """
    if app.config.get("TESTING"):
        # Don't set up file logging during tests
        return

    # Remove default handlers to avoid duplicate logs
    for handler in app.logger.handlers:
        app.logger.removeHandler(handler)

    # Set up a rotating file handler
    log_file = app.config.get("LOG_FILE", "app.log")
    # Rotate logs after 1MB, keep 5 backup logs
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=1024 * 1024, backupCount=5
    )

    # Use JSON formatter for structured logs
    formatter = JsonFormatter()
    file_handler.setFormatter(formatter)

    # Set log level from config, default to INFO
    log_level = app.config.get("LOG_LEVEL", logging.INFO)
    file_handler.setLevel(log_level)

    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)
    app.logger.info("Structured logging configured.")


@error_handler_bp.app_errorhandler(HTTPException)
def handle_http_exception(e):
    """Handles all standard HTTP exceptions (e.g., 404, 405)."""
    current_app.logger.warning(
        f"HTTP Exception caught: {e.code} {e.name} for URL {request.path}"
    )
    response = jsonify({"error": {"code": e.code, "message": e.name}})
    response.status_code = e.code
    return response


@error_handler_bp.app_errorhandler(NotFoundException)
def handle_not_found(error):
    """Handles our custom NotFoundException and returns a 404."""
    current_app.logger.info(f"Resource not found at {request.path}: {error}")
    response = jsonify(
        {
            "error": {
                "code": 404,
                "message": str(error) or "The requested resource was not found.",
            }
        }
    )
    response.status_code = 404
    return response


@error_handler_bp.app_errorhandler(ValidationException)
def handle_validation_error(error):
    """Handles our custom ValidationException and returns a 400."""
    current_app.logger.warning(
        f"Validation failed for request to {request.path}: {error}"
    )
    response = jsonify(
        {
            "error": {
                "code": 400,
                "message": str(error) or "A validation error occurred.",
            }
        }
    )
    response.status_code = 400
    return response


@error_handler_bp.app_errorhandler(AuthorizationException)
def handle_authorization_error(error):
    """Handles our custom AuthorizationException and returns a 403."""
    current_app.logger.warning(
        f"Authorization failed for request to {request.path}: {error}"
    )
    response = jsonify(
        {
            "error": {
                "code": 403,
                "message": str(error)
                or "You do not have permission to perform this action.",
            }
        }
    )
    response.status_code = 403
    return response


@error_handler_bp.app_errorhandler(ValidationError)
def handle_marshmallow_validation_error(error):
    """Handles Marshmallow-specific validation errors for structured details."""
    current_app.logger.warning(
        f"Marshmallow schema validation failed: {error.messages}"
    )
    response = jsonify(
        {
            "error": {
                "code": 400,
                "message": "Input validation failed.",
                "details": error.messages,
            }
        }
    )
    response.status_code = 400
    return response


@error_handler_bp.app_errorhandler(Exception)
def handle_generic_exception(e):
    """
    Catch-all handler for any unhandled exceptions to ensure a 500 response.
    This is a critical safety net.
    """
    # Log the full traceback for debugging
    current_app.logger.critical(
        f"Unhandled exception at {request.path}: {e}", exc_info=True
    )

    response = jsonify(
        {
            "error": {
                "code": 500,
                "message": "An unexpected internal server error occurred.",
            }
        }
    )
    response.status_code = 500
    return response


def register_error_handlers(app):
    """Registers the error handler blueprint and security headers with the app."""
    app.register_blueprint(error_handler_bp)

    @app.after_request
    def add_security_headers(response):
        """Add common security headers to every response."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response
