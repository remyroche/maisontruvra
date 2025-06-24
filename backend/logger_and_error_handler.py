import os
import logging
import traceback
from logging.handlers import RotatingFileHandler
from flask import jsonify

# Assuming ServiceError is a custom exception defined in your services/exceptions.py
from backend.services.exceptions import ServiceError

class Loggin

# Logging Setup
    if not os.path.exists('logs'):
        os.mkdir('logs')

    # General Application Logger
    file_handler = RotatingFileHandler('logs/backend.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    # Security Events Logger
    security_handler = RotatingFileHandler('logs/security.log', maxBytes=10240, backupCount=10)
    security_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    security_logger = logging.getLogger('security')
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.INFO)

    app.logger.info('Maison Truvra backend startup')

    # --- Global Exception Handler ---
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Log unhandled exceptions."""
        # Get the full traceback
        tb_str = traceback.format_exc()
        app.logger.error(f"Unhandled Exception: {e}\nTraceback:\n{tb_str}")
        
        # In a production environment, you might want a more generic error message
        response = {
            "error": "An internal server error occurred.",
            "message": str(e) # Optional: include error message in dev but not prod
        }
        return jsonify(response), 500


    # 1. Global Error Handler for our custom ServiceError
    @app.errorhandler(ServiceError)
    def handle_service_error(error):
        """Catches custom service layer errors and returns a clean JSON response."""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        app.logger.warning(f"Service Error: {error.message} (Status Code: {error.status_code})")
        return response

    # 2. Global Error Handler for all other unhandled exceptions
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Catches any unhandled exceptions to prevent crashes and log them."""
        # In production, you would not want to expose the raw error message.
        # This is a safe, generic response.
        response = jsonify({"error": "An internal server error occurred.", "status_code": 500})
        response.status_code = 500
        # Log the full exception for debugging.
        app.logger.error(f"Unhandled Exception: {error}", exc_info=True)
        return response

    # 3. Configure Production-Grade Logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        # Log to a rotating file to prevent the log file from becoming too large.
        file_handler = RotatingFileHandler('logs/maison-truvra.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Maison Truv-ra startup')

    
