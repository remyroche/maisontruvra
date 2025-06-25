import traceback
from flask import jsonify, request

# Import centralized loggers
from backend.loggers import security_logger, setup_logging


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
