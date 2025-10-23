"""
Standardized Error Handling Utilities

This module provides standardized error handling patterns and utilities
for consistent error responses across the application.
"""

from flask import jsonify, request, current_app
from werkzeug.exceptions import HTTPException
from ..services.exceptions import (
    ServiceException,
    ValidationException,
    NotFoundException,
    AuthenticationException,
    AuthorizationException,
    DataConflictException
)
import logging

logger = logging.getLogger(__name__)


class ErrorResponse:
    """Standardized error response format."""
    
    @staticmethod
    def create_error_response(
        error_type: str,
        message: str,
        details: dict = None,
        status_code: int = 500,
        request_id: str = None
    ) -> tuple:
        """
        Create a standardized error response.
        
        Args:
            error_type (str): Type of error (e.g., 'validation_error', 'not_found')
            message (str): Human-readable error message
            details (dict): Additional error details
            status_code (int): HTTP status code
            request_id (str): Request ID for tracking
            
        Returns:
            tuple: (response_dict, status_code)
        """
        response = {
            'error': {
                'type': error_type,
                'message': message,
                'timestamp': current_app.logger.handlers[0].formatter.formatTime(
                    current_app.logger.handlers[0].formatter.converter()
                ) if current_app.logger.handlers else None,
                'request_id': request_id or getattr(request, 'id', None)
            }
        }
        
        if details:
            response['error']['details'] = details
        
        return response, status_code
    
    @staticmethod
    def validation_error(message: str, field_errors: dict = None, request_id: str = None):
        """Create a validation error response."""
        details = {'field_errors': field_errors} if field_errors else None
        return ErrorResponse.create_error_response(
            'validation_error',
            message,
            details,
            400,
            request_id
        )
    
    @staticmethod
    def not_found(resource: str, identifier: str = None, request_id: str = None):
        """Create a not found error response."""
        message = f"{resource} not found"
        if identifier:
            message += f" with identifier: {identifier}"
        
        return ErrorResponse.create_error_response(
            'not_found',
            message,
            {'resource': resource, 'identifier': identifier},
            404,
            request_id
        )
    
    @staticmethod
    def authentication_error(message: str = "Authentication required", request_id: str = None):
        """Create an authentication error response."""
        return ErrorResponse.create_error_response(
            'authentication_error',
            message,
            None,
            401,
            request_id
        )
    
    @staticmethod
    def authorization_error(message: str = "Insufficient permissions", request_id: str = None):
        """Create an authorization error response."""
        return ErrorResponse.create_error_response(
            'authorization_error',
            message,
            None,
            403,
            request_id
        )
    
    @staticmethod
    def conflict_error(message: str, details: dict = None, request_id: str = None):
        """Create a conflict error response."""
        return ErrorResponse.create_error_response(
            'conflict_error',
            message,
            details,
            409,
            request_id
        )
    
    @staticmethod
    def internal_error(message: str = "Internal server error", request_id: str = None):
        """Create an internal server error response."""
        return ErrorResponse.create_error_response(
            'internal_error',
            message,
            None,
            500,
            request_id
        )


def handle_service_exception(e: ServiceException, request_id: str = None):
    """
    Handle service exceptions and convert them to standardized responses.
    
    Args:
        e (ServiceException): The service exception
        request_id (str): Request ID for tracking
        
    Returns:
        tuple: (response_dict, status_code)
    """
    if isinstance(e, ValidationException):
        return ErrorResponse.validation_error(
            e.message,
            getattr(e, 'field_errors', None),
            request_id
        )
    elif isinstance(e, NotFoundException):
        return ErrorResponse.not_found(
            getattr(e, 'resource', 'Resource'),
            getattr(e, 'identifier', None),
            request_id
        )
    elif isinstance(e, AuthenticationException):
        return ErrorResponse.authentication_error(e.message, request_id)
    elif isinstance(e, AuthorizationException):
        return ErrorResponse.authorization_error(e.message, request_id)
    elif isinstance(e, DataConflictException):
        return ErrorResponse.conflict_error(e.message, request_id)
    else:
        return ErrorResponse.internal_error(e.message, request_id)


def handle_http_exception(e: HTTPException, request_id: str = None):
    """
    Handle HTTP exceptions and convert them to standardized responses.
    
    Args:
        e (HTTPException): The HTTP exception
        request_id (str): Request ID for tracking
        
    Returns:
        tuple: (response_dict, status_code)
    """
    error_type_map = {
        400: 'bad_request',
        401: 'authentication_error',
        403: 'authorization_error',
        404: 'not_found',
        409: 'conflict_error',
        422: 'validation_error',
        500: 'internal_error'
    }
    
    error_type = error_type_map.get(e.code, 'http_error')
    
    return ErrorResponse.create_error_response(
        error_type,
        e.description or "An error occurred",
        None,
        e.code,
        request_id
    )


def handle_unexpected_exception(e: Exception, request_id: str = None):
    """
    Handle unexpected exceptions and convert them to standardized responses.
    
    Args:
        e (Exception): The unexpected exception
        request_id (str): Request ID for tracking
        
    Returns:
        tuple: (response_dict, status_code)
    """
    logger.error(f"Unexpected error: {str(e)}", exc_info=True)
    
    return ErrorResponse.create_error_response(
        'internal_error',
        "An unexpected error occurred",
        {'exception_type': type(e).__name__} if current_app.debug else None,
        500,
        request_id
    )


def log_error(error: Exception, context: str = None, request_id: str = None):
    """
    Log errors with consistent formatting.
    
    Args:
        error (Exception): The error to log
        context (str): Additional context about where the error occurred
        request_id (str): Request ID for tracking
    """
    error_info = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'request_id': request_id or getattr(request, 'id', None),
        'context': context
    }
    
    if isinstance(error, ServiceException):
        logger.warning(f"Service error: {error_info}")
    else:
        logger.error(f"Unexpected error: {error_info}", exc_info=True)