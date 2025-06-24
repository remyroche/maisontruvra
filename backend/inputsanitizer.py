# backend/inputsanitizer.py

from functools import wraps
from flask import request, g, jsonify, Flask
import logging
import bleach # Robust HTML sanitization library
from collections import Mapping # For Python 3.9+ use collections.abc.Mapping

# Configure logging
logger = logging.getLogger(__name__)
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO) # Adjust as needed (DEBUG, INFO, WARNING, ERROR)

class InputSanitizer:
    """
    Provides methods for sanitizing various types of input data,
    primarily focusing on preventing XSS.
    """
    @staticmethod
    def sanitize_string(text: str) -> str:
        """
        Sanitizes a string using the bleach library to prevent XSS attacks.
        Strips all HTML tags by default and escapes dangerous characters.
        """
        if not isinstance(text, str):
            # If it's not a string, return as is. Validation should catch type errors later.
            return text
        
        # Configure allowed HTML tags and attributes.
        # For strict prevention in API inputs, it's often best to allow nothing.
        allowed_tags = []  # No HTML tags allowed
        allowed_attributes = {} # No attributes allowed

        sanitized_text = bleach.clean(
            text,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True, # Removes tags not in allowed_tags
            # Bleach also escapes default HTML entities (<, >, ", ', &)
        )
        return sanitized_text

    @staticmethod
    def recursive_sanitize(data):
        """
        Recursively sanitizes string values within dictionaries and lists
        using sanitize_string.
        """
        if isinstance(data, Mapping): # Use Mapping for dict-like objects
            return {key: InputSanitizer.recursive_sanitize(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [InputSanitizer.recursive_sanitize(element) for element in data]
        elif isinstance(data, str):
            return InputSanitizer.sanitize_string(data)
        else:
            return data

def sanitize_json_request_data():
    """
    Flask before_request hook to sanitize JSON request bodies.
    It recursively sanitizes all string values within the JSON payload
    and stores the sanitized version in `g.sanitized_json`.
    It also attempts to overwrite Flask's internal cached JSON for `request.json`.
    """
    if request.method in ['POST', 'PUT', 'PATCH']:
        if request.is_json and request.json is not None:
            try:
                sanitized_data = InputSanitizer.recursive_sanitize(request.json)
                g.sanitized_json = sanitized_data
                
                # Attempt to overwrite Flask's cached JSON for subsequent `request.json` calls
                # This is a low-level Flask detail and might not be future-proof,
                # but currently effective. g.sanitized_json is the most reliable way.
                request._cached_json = (sanitized_data, request._cached_json[1])
                security_logger.debug("JSON request data sanitized and overwritten.")
            except Exception as e:
                security_logger.error(f"Error sanitizing JSON request data: {e}", exc_info=True)
                # Decide if you want to abort here or let the route handle it.
                # For critical APIs, you might return jsonify({"error": "Invalid input format"}), 400
                pass # Continue, but data might not be fully sanitized if an error occurred

def sanitize_form_request_data():
    """
    Flask before_request hook to sanitize HTML form data (`request.form`).
    It sanitizes all string values in the form data and stores the
    sanitized version in `g.sanitized_form`.
    """
    if request.method in ['POST', 'PUT', 'PATCH']:
        # Check if it's form data (application/x-www-form-urlencoded or multipart/form-data)
        if request.form:
            try:
                sanitized_form_data = InputSanitizer.recursive_sanitize(request.form.to_dict(flat=False))
                g.sanitized_form = sanitized_form_data
                security_logger.debug("Form request data sanitized.")
            except Exception as e:
                security_logger.error(f"Error sanitizing form request data: {e}", exc_info=True)
                pass # Continue

def sanitize_url_params():
    """
    Flask before_request hook to sanitize URL query parameters (`request.args`).
    It sanitizes all string values in the query parameters and stores the
    sanitized version in `g.sanitized_args`.
    """
    if request.args:
        try:
            sanitized_args = InputSanitizer.recursive_sanitize(request.args.to_dict(flat=False))
            g.sanitized_args = sanitized_args
            security_logger.debug("URL query parameters sanitized.")
        except Exception as e:
            security_logger.error(f"Error sanitizing URL query parameters: {e}", exc_info=True)
            pass # Continue

def init_app_middleware(app: Flask):
    """
    Registers the sanitization middleware with the Flask application.
    """
    app.before_request(sanitize_json_request_data)
    app.before_request(sanitize_form_request_data)
    app.before_request(sanitize_url_params)
    security_logger.info("Input sanitization middleware registered.")
