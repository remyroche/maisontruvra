import logging
import uuid
from logging.handlers import RotatingFileHandler

from flask import g, jsonify, request
from werkzeug.exceptions import HTTPException


def setup_logging(app):
    """
    Configures application-wide logging, including request correlation IDs.
    """
    # Remove default handlers to avoid duplicate logs
    for handler in app.logger.handlers:
        app.logger.removeHandler(handler)

    # Configure formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - RequestID: %(request_id)s - %(message)s [in %(pathname)s:%(lineno)d]"
    )

    # File handler
    file_handler = RotatingFileHandler("backend_app.log", maxBytes=10000, backupCount=3)
    file_handler.setFormatter(formatter)

    # Console handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Add handlers to the app's logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)

    @app.before_request
    def before_request_logging():
        """
        Log before each request and assign a unique request ID.
        """
        # FIX: Added import for 'uuid'
        g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Add a filter to inject the request_id into all log records
        class RequestIdFilter(logging.Filter):
            def filter(self, record):
                record.request_id = g.get("request_id", "N/A")
                return True

        app.logger.addFilter(RequestIdFilter())
        app.logger.info(f"Request started: {request.method} {request.path}")

    @app.after_request
    def after_request_logging(response):
        """
        Log after each request.
        """
        app.logger.info(
            f"Request finished: {request.method} {request.path} - Status: {response.status_code}"
        )
        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        """
        Handles and logs all unhandled exceptions.
        """
        # FIX: Added import for 'HTTPException' from 'werkzeug.exceptions'
        # Pass through HTTP exceptions (like 404, 401, etc.)
        if isinstance(e, HTTPException):
            return e

        # Handle non-HTTP exceptions
        logger = logging.getLogger("backend.unhandled")
        logger.error(f"Unhandled exception: {e}", exc_info=True)

        # FIX: Added import for 'jsonify' from 'flask'
        return jsonify(error="An unexpected server error occurred."), 500
