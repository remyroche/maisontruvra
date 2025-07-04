"""
Centralized logging configuration for the application.
This module defines all loggers used throughout the application to ensure consistency.
"""

import json
import logging
from logging.config import dictConfig

from flask import g, request

# Create loggers
app_logger = logging.getLogger("app")
security_logger = logging.getLogger("security")
database_logger = logging.getLogger("database")
api_logger = logging.getLogger("api")

# Set default levels
security_logger.setLevel(logging.INFO)
database_logger.setLevel(logging.INFO)


class RequestIDFilter(logging.Filter):
    """
    A logging filter that injects the request ID into log records.

    This class is used to add contextual information from the request,
    specifically a unique request ID and the request endpoint, to each log
    entry. This is invaluable for tracing and debugging.
    """

    def filter(self, record):
        """
        Adds the request ID and endpoint to the log record.

        If a request ID is present in Flask's 'g' object, it's added
        to the log record. Otherwise, a default value is used.
        """
        record.request_id = g.get("request_id", "no-request-id")
        record.endpoint = request.path if request else "not-in-request-context"
        return True


# Configuration for the application's logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id_filter": {
            "()": RequestIDFilter,
        }
    },
    "formatters": {
        "standard": {
            # Added %(request_id)s and %(endpoint)s to the log format
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s [request_id:%(request_id)s endpoint:%(endpoint)s]"
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "filters": ["request_id_filter"],  # Apply the filter to this handler
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "app.log",
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "standard",
            "filters": ["request_id_filter"],  # Apply the filter to this handler
        },
        "security": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "security.log",
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "standard",
            "filters": ["request_id_filter"],  # Apply the filter to this handler
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "app_logger": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "security_logger": {
            "handlers": ["console", "security"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}


class JsonFormatter(logging.Formatter):
    """
    Formats log records as JSON strings.
    """

    def format(self, record):
        log_object = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
        }
        if record.exc_info:
            log_object["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_object)


def setup_logging(app):
    """
    Configures comprehensive logging for the Flask application.
    """
    # Apply the configuration from the dictionary
    dictConfig(LOGGING_CONFIG)

    # Add a request ID to each log message for better traceability
    @app.before_request
    def before_request_logging():
        if "X-Request-ID" in request.headers:
            g.request_id = request.headers["X-Request-ID"]
        else:
            g.request_id = str(uuid.uuid4())

    # After request, log details about the response
    @app.after_request
    def after_request_logging(response):
        if request.path.startswith("/static"):
            return response

        logger = logging.getLogger("backend")
        logger.info(
            f"{request.remote_addr} - {request.method} {request.path} - {response.status_code}"
        )
        return response

    # Handle exceptions by logging them
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Pass through HTTP exceptions
        if isinstance(e, HTTPException):
            return e

        logger = logging.getLogger("backend")
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        return jsonify(error="An unexpected error occurred."), 500


__all__ = [
    "app_logger",
    "security_logger",
    "database_logger",
    "api_logger",
    "setup_logging",
]
