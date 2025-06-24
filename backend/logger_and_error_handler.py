import os
import logging
import traceback
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request # Import 'request' to access request details
from backend.services.exceptions import ServiceError



def logging_and_error_handling():
    """
    Configures logging and global error handlers for the Flask application.

    Args:
        app: The Flask application instance.
    """

    # --- Configuration for Logging ---
    # Use environment variables or a config file for these in a real app
    LOGS_DIR = os.environ.get('LOGS_DIR', 'logs')
    APP_LOG_FILE = os.path.join(LOGS_DIR, 'backend.log')
    SECURITY_LOG_FILE = os.path.join(LOGS_DIR, 'security.log')
    MAX_LOG_BYTES = 10240 # 10KB
    BACKUP_COUNT = 10

    # Ensure logs directory exists
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR) # Use makedirs to create intermediate directories if they don't exist

    # --- Streamlined Logging Setup ---

    # Configure the general application logger
    log_level = logging.INFO
    if app.debug or app.testing:
        log_level = logging.DEBUG # More verbose logging in dev/test

    # Remove default handlers to prevent duplicate logs (e.g., to console)
    # This loop is crucial for preventing multiple handlers being added on reloads
    for handler in list(app.logger.handlers):
        app.logger.removeHandler(handler)

    # General Application Logger - Rotating File
    file_handler = RotatingFileHandler(APP_LOG_FILE, maxBytes=MAX_LOG_BYTES, backupCount=BACKUP_COUNT)
    # Adding more context to the formatter
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d] - Request ID: %(request_id)s'))
    file_handler.setLevel(log_level)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)

    # Security Events Logger - Separate Rotating File
    security_handler = RotatingFileHandler(SECURITY_LOG_FILE, maxBytes=MAX_LOG_BYTES, backupCount=BACKUP_COUNT)
    security_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s - Request ID: %(request_id)s'))
    security_logger = logging.getLogger('security') # Get or create the security logger
    # Ensure security_logger also has its default handlers removed if reloaded
    for handler in list(security_logger.handlers):
    security_logger.removeHandler(handler)
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.INFO)

    # Optional: Add console handler for development
    if app.debug:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d] - Request ID: %(request_id)s'))
        console_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(console_handler) # Add to app.logger
        # If you want security logs to also go to console in debug:
        # security_logger.addHandler(console_handler)

    app.logger.info('Maison Truvra backend startup (logging configured)')

    # --- Request Context for Logging (Pre-request hook) ---
    # This helps add unique IDs to each request's log messages
    # This filter ensures 'request_id' is available in log records
    class RequestIDFilter(logging.Filter):
        def filter(self, record):
            # Try to get request_id from Flask's request context
            # Use a default 'N/A' if not in request context (e.g., for startup logs)
            record.request_id = getattr(request, 'request_id', 'N/A')
            return True

    app.logger.addFilter(RequestIDFilter())
    security_logger.addFilter(RequestIDFilter()) # Apply filter to security logger too

    @app.before_request
    def set_request_id():
        # Generate a unique request ID (e.g., UUID4) or use one from headers
        # os.urandom(8).hex() provides a random 16-character hex string
        request.request_id = os.urandom(8).hex()


    # --- Global Exception Handlers ---

    # 1. Global Error Handler for our custom ServiceError
    @app.errorhandler(ServiceError)
    def handle_service_error(error):
        """
        Catches custom service layer errors and returns a clean JSON response.
        Logs the error with relevant details.
        """
        response_payload = error.to_dict()
        response_payload.pop('traceback', None) # Don't expose internal traceback to client
        response = jsonify(response_payload)
        response.status_code = error.status_code

        request_id = getattr(request, 'request_id', 'N/A')
        app.logger.warning(
            f"Service Error: {error.message} (Status Code: {error.status_code}, Request ID: {request_id})",
            extra={'error_code': error.error_code, 'details': error.details, 'request_id': request_id} # Add structured data
        )
        return response

    # 2. Global Error Handler for all other unhandled exceptions (consolidated and improved)
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """
        Catches any unhandled exceptions to prevent crashes and log them exhaustively.
        Provides a generic error response to the client.
        """
        tb_str = traceback.format_exc() # Get full traceback
        request_id = getattr(request, 'request_id', 'N/A')

        app.logger.error(
            f"Unhandled Exception caught for Request ID: {request_id}\n"
            f"Path: {request.path}\n"
            f"Method: {request.method}\n"
            f"Error: {error}\n"
            f"Traceback:\n{tb_str}",
            exc_info=True # This automatically logs exception info including stack trace
        )

        # Generic response for unexpected errors in production
        response = jsonify({"error": "An internal server error occurred.", "status_code": 500})
        response.status_code = 500
        return response

    # --- Optional: Custom handlers for common HTTP errors ---
    @app.errorhandler(404)
    def not_found_error(error):
        request_id = getattr(request, 'request_id', 'N/A')
        app.logger.warning(
            f"404 Not Found: {request.path} (Request ID: {request_id})"
        )
        return jsonify({"error": "Resource not found", "status_code": 404}), 404

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        request_id = getattr(request, 'request_id', 'N/A')
        app.logger.warning(
            f"405 Method Not Allowed: {request.method} {request.path} (Request ID: {request_id})"
        )
        return jsonify({"error": "Method not allowed", "status_code": 405}), 405


    
