# backend/logger_and_error_handler.py
"""
This module sets up application-wide logging and global error handlers.
Centralizing error handling ensures consistent error responses across the API.
"""
import logging
from flask import jsonify
from werkzeug.exceptions import HTTPException
from backend.services.exceptions import ApiServiceError
from marshmallow import ValidationError

def register_error_handlers(app):
    """
    Registers global error handlers for the Flask application.

    Args:
        app (Flask): The Flask application instance.
    """

    # Configure logging (assuming basic setup is sufficient)
    logging.basicConfig(level=logging.INFO)
    
    @app.errorhandler(ApiServiceError)
    def handle_api_service_error(error):
        """
        Handles all custom service layer exceptions derived from ApiServiceError.
        """
        app.logger.warning(f"API Service Error: {error.message} (Status: {error.status_code})")
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """
        Handles Marshmallow validation errors, returning a 400 Bad Request
        with a structured list of errors.
        """
        app.logger.warning(f"Input validation failed: {error.messages}")
        response = jsonify({"message": "Input validation failed", "errors": error.messages})
        response.status_code = 400
        return response

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """
        Handles standard HTTP exceptions (e.g., 404 Not Found, 405 Method Not Allowed).
        """
        app.logger.error(f"HTTP Exception: {e.code} {e.name} - {e.description}")
        response = e.get_response()
        # Ensure the response is JSON
        response.data = jsonify({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }).data
        response.content_type = "application/json"
        return response

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        """
        A catch-all handler for any other unhandled exceptions.
        This prevents stack traces from being leaked to the client.
        """
        app.logger.critical(f"Unhandled Exception: {str(e)}", exc_info=True)
        response = jsonify({
            "message": "An internal server error occurred.",
            # Avoid leaking internal error details in production
            "error": str(e) if app.debug else "Internal Server Error"
        })
        response.status_code = 500
        return response
