
class ServiceError(Exception):
    """Base exception for service layer errors."""
    status_code = 500
    message = "An internal service error occurred."

    def __init__(self, message=None, status_code=None):
        super().__init__()
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code

class NotFoundException(ServiceError):
    """Exception raised when a resource is not found."""
    status_code = 404

class ValidationException(ServiceError):
    """Exception raised when validation fails."""
    status_code = 400

class UnauthorizedException(ServiceError):
    """Exception raised when user is not authorized."""
    status_code = 401
# backend/services/exceptions.py
"""
This module defines custom exception classes for the service layer.
Using specific exceptions allows for more granular error handling and clearer
API responses.
"""

class ApiServiceError(Exception):
    """Base class for service layer exceptions."""
    status_code = 500
    message = "An unexpected error occurred."

    def __init__(self, message=None, status_code=None, payload=None):
        """
        Initializes the ApiServiceError.
        Args:
            message (str, optional): The error message. Defaults to None.
            status_code (int, optional): The HTTP status code. Defaults to None.
            payload (dict, optional): Additional data to include in the error response. Defaults to None.
        """
        super().__init__(message)
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """Converts the exception to a dictionary for JSON serialization."""
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

class InvalidAPIRequestError(ApiServiceError):
    """Raised when an API request is invalid or missing required data."""
    status_code = 400

class ProductNotFoundError(ApiServiceError):
    """Raised when a requested product or variant is not found."""
    status_code = 404

class DuplicateProductError(ValidationException):
    """Raised when trying to create a product that already exists."""
    pass
    
class InvalidAPIRequestError(ValidationException):
    """Raised for general invalid API requests."""
    pass

class AuthorizationException(ServiceError):
    """
    Raised when a user is not authorized to perform an action or access a resource.
    This should result in a 403 Forbidden response.
    """
    pass

class DuplicateProductError(ApiServiceError):
    """Raised when a product with the same name or SKU already exists."""
    status_code = 409 # 409 Conflict

class InsufficientStockError(ApiServiceError):
    """Raised when there is not enough stock for an operation."""
    status_code = 400

class DuplicateEmailError(ApiServiceError):
    """Raised when a user with the given email already exists during registration."""
    status_code = 409 # 409 Conflict

class AuthenticationError(ApiServiceError):
    """Raised for authentication failures, such as invalid credentials."""
    status_code = 401
    
class InvalidPasswordException(ValidationException):
    """Exception for password policy failures."""
    pass

class InvalidUsageException(ServiceError):
    """Exception for invalid usage of service methods."""
    status_code = 400

class ServiceException(Exception):
    """Base exception for services."""
    def __init__(self, message="An internal error occurred."):
        self.message = message
        super().__init__(self.message)

class ResourceNotFound(ServiceException):
    """Raised when a resource is not found."""
    def __init__(self, resource_name="Resource", resource_id=None):
        message = f"{resource_name} not found."
        if resource_id:
            message = f"{resource_name} with ID '{resource_id}' not found."
        super().__init__(message)

class AuthorizationError(ServiceException):
    """Raised when an action is not authorized."""
    def __init__(self, message="You are not authorized to perform this action."):
        super().__init__(message)

class ValidationError(ServiceException):
    """Raised on data validation errors."""
    pass

class CheckoutValidationError(ServiceException):
    """Raised when checkout validation fails (e.g., stock or price change)."""
    def __init__(self, message="Checkout validation failed."):
        self.message = message
        super().__init__(self.message)

class UserNotFoundException(ServiceError):
    """Raised when a user is not found."""
    status_code = 404

class UpdateException(ServiceError):
    """Raised when an update operation fails."""
    status_code = 400

class DeletionException(ServiceError):
    """Raised when a deletion operation fails."""
    status_code = 400



