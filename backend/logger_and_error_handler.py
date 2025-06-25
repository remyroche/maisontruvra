import logging
from logging.handlers import TimedRotatingFileHandler
import os
import json
import traceback
from flask import jsonify, request

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
            log_object['exc_info'] = self.formatException(record.exc_info)
        return json.dumps(log_object)

def setup_logging(app):
    """
    Configures comprehensive logging for the Flask application.
    """
    if not app.debug and not app.testing:
        # Get configuration from app config
        log_dir = app.config.get('LOG_DIR', 'logs')
        log_level_str = app.config.get('LOG_LEVEL', 'INFO').upper()
        log_level = getattr(logging, log_level_str, logging.INFO)
        use_json_formatter = app.config.get('USE_JSON_LOGS', False)

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # File Handler with daily rotation
        file_handler = TimedRotatingFileHandler(
            os.path.join(log_dir, 'app.log'), when='midnight', interval=1, backupCount=30
        )

        if use_json_formatter:
            formatter = JsonFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            )
        
        file_handler.setFormatter(formatter)
        
        # Console handler for simple output
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)
        app.logger.setLevel(log_level)
        app.logger.info('Application Logging Started')


def register_error_handlers(app):
    """
    Registers centralized error handlers for the Flask application.
    """
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f"404 Not Found: {request.path}")
        return jsonify({"error": "Not Found", "message": "The requested URL was not found on the server."}), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning(f"403 Forbidden: Access denied to {request.path} for user.")
        return jsonify({"error": "Forbidden", "message": "You don't have the permission to access the requested resource."}), 403

    @app.errorhandler(401)
    def unauthorized_error(error):
        app.logger.warning(f"401 Unauthorized: Unauthorized access attempt to {request.path}.")
        return jsonify({"error": "Unauthorized", "message": "Authentication is required to access this resource."}), 401

    @app.errorhandler(Exception)
    def generic_error_handler(error):
        """
        Handles all unhandled exceptions, logs them in detail, and returns a
        generic 500 error to the client.
        """
        error_traceback = traceback.format_exc()
        app.logger.error(
            f"Unhandled Exception: {error}\n"
            f"Path: {request.path}\n"
            f"Method: {request.method}\n"
            f"IP: {request.remote_addr}\n"
            f"Traceback:\n{error_traceback}"
        )
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. The administrators have been notified."
        }), 500
