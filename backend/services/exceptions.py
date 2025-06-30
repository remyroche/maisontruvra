
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



