
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

# Legacy aliases for backward compatibility
ServiceException = ServiceError
