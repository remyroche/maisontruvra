# backend/utils/input_sanitizer.py
"""
Centralized input sanitization utilities for the application.
This module provides a unified InputSanitizer class that combines functionality
from both previous implementations.
"""

from typing import Any, Dict, List, Union, Optional
import re
import bleach
from collections.abc import Mapping
from markupsafe import Markup
from flask import request, g
from backend.services.exceptions import ValidationException
from backend.loggers import security_logger

class InputSanitizer:
    """
    Provides methods for sanitizing various types of input data,
    primarily focusing on preventing XSS and injection attacks.
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
        
        # Additional sanitization for script patterns
        sanitized = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', sanitized_text, flags=re.IGNORECASE)
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    @staticmethod
    def sanitize_html(dirty_html: str, allow_tags: bool = False) -> str:
        """
        Sanitize HTML content using bleach.
        
        Args:
            dirty_html: The HTML content to sanitize
            allow_tags: If True, allows a limited set of safe HTML tags
            
        Returns:
            Sanitized HTML string
        """
        if not dirty_html:
            return ""
        
        if allow_tags:
            # Only allow these safe tags when explicitly requested
            allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'h1', 'h2', 'h3']
            allowed_attributes = {}
        else:
            # Default is to strip all HTML
            allowed_tags = []
            allowed_attributes = {}
        
        clean_html = bleach.clean(
            dirty_html,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
        return clean_html
    
    @staticmethod
    def recursive_sanitize(data: Any) -> Any:
        """
        Recursively sanitizes string values within dictionaries and lists
        using sanitize_string.
        
        Args:
            data: The data structure to sanitize (dict, list, or string)
            
        Returns:
            Sanitized data structure of the same type
        """
        if isinstance(data, Mapping): # Use Mapping for dict-like objects
            return {key: InputSanitizer.recursive_sanitize(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [InputSanitizer.recursive_sanitize(element) for element in data]
        elif isinstance(data, str):
            return InputSanitizer.sanitize_string(data)
        else:
            return data
    
    @staticmethod
    def sanitize_input(data: Any) -> Any:
        """
        Alias for recursive_sanitize for backward compatibility.
        
        Args:
            data: The data structure to sanitize (dict, list, or string)
            
        Returns:
            Sanitized data structure of the same type
        """
        return InputSanitizer.recursive_sanitize(data)
    
    @staticmethod
    def validate_email(email: str) -> str:
        """
        Validate email format.
        
        Args:
            email: The email address to validate
            
        Returns:
            Normalized email address (lowercase, trimmed)
            
        Raises:
            ValidationException: If the email format is invalid
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationException("Invalid email format")
        return email.lower().strip()
    
    @staticmethod
    def sanitize_sql_input(input_value: str) -> str:
        """
        Sanitize input for SQL queries (though parameterized queries are preferred).
        
        Args:
            input_value: The string to sanitize
            
        Returns:
            Sanitized string with SQL injection patterns removed
        """
        if not input_value:
            return ""
        
        # Remove SQL injection patterns
        dangerous_patterns = [
            r'(\b(ALTER|CREATE|DELETE|DROP|EXEC(UTE)?|INSERT|SELECT|UNION|UPDATE)\b)',
            r'(\b(SCRIPT|JAVASCRIPT|VBSCRIPT|ONLOAD|ONERROR)\b)',
            r'([\'\";])',
            r'(\-\-)',
            r'(\/\*|\*\/)'
        ]
        
        sanitized = str(input_value)
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()


# Flask request middleware functions

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

def init_app_middleware(app):
    """
    Registers the sanitization middleware with the Flask application.
    """
    app.before_request(sanitize_json_request_data)
    app.before_request(sanitize_form_request_data)
    app.before_request(sanitize_url_params)
    security_logger.info("Input sanitization middleware registered.")


# Decorator for route-level sanitization
def sanitize_request_data(f):
    """
    Decorator to sanitize all incoming request data (JSON, form, and query args).
    This is a proactive security measure against XSS and other injection attacks.
    """
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # JSON body is now globally sanitized by `sanitize_json_request_data` middleware,
        # and request._cached_json is overwritten.

        # This part handles form data if not globally handled:
        if request.form:
            sanitized_form = {key: InputSanitizer.sanitize_string(value) for key, value in request.form.items()}
            g.sanitized_form = sanitized_form # Store in g for access

        # This part handles query arguments:
        if request.args:
            sanitized_args = {key: InputSanitizer.sanitize_string(value) for key, value in request.args.items()}
            g.sanitized_args = sanitized_args # Store in g for access

        return f(*args, **kwargs)
    return decorated_function

__all__ = [
    'InputSanitizer', 
    'sanitize_json_request_data', 
    'sanitize_form_request_data', 
    'sanitize_url_params',
    'init_app_middleware',
    'sanitize_request_data'
]
