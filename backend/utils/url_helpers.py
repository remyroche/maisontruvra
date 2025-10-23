"""
Secure URL Generation Utilities

This module provides secure URL generation functions that prevent Host header injection
by using trusted configuration values instead of relying on request headers.
"""

from flask import current_app
from urllib.parse import urljoin


def get_secure_base_url():
    """
    Get the base URL from configuration, ensuring it's trusted and not from request headers.
    
    Returns:
        str: The base URL from configuration
    """
    base_url = current_app.config.get('BASE_URL', 'http://127.0.0.1:5000')
    
    # Ensure the URL ends with a slash for proper joining
    if not base_url.endswith('/'):
        base_url += '/'
    
    return base_url


def generate_secure_url(endpoint, **values):
    """
    Generate a secure external URL by combining trusted base URL with Flask's url_for.
    
    Args:
        endpoint (str): The Flask endpoint name
        **values: Values to pass to url_for
        
    Returns:
        str: A secure external URL
    """
    from flask import url_for
    
    # Generate the internal URL using Flask's url_for
    internal_url = url_for(endpoint, **values)
    
    # Combine with trusted base URL
    base_url = get_secure_base_url()
    return urljoin(base_url, internal_url.lstrip('/'))


def generate_verification_url(token, endpoint='auth.verify_email'):
    """
    Generate a secure verification URL for email verification.
    
    Args:
        token (str): The verification token
        endpoint (str): The Flask endpoint for verification
        
    Returns:
        str: A secure verification URL
    """
    return generate_secure_url(endpoint, token=token)


def generate_password_reset_url(token, endpoint='auth.reset_password'):
    """
    Generate a secure password reset URL.
    
    Args:
        token (str): The password reset token
        endpoint (str): The Flask endpoint for password reset
        
    Returns:
        str: A secure password reset URL
    """
    return generate_secure_url(endpoint, token=token)