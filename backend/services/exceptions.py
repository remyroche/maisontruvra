
class ServiceException(Exception):
    """Base exception for service layer errors."""
    pass

class NotFoundException(ServiceException):
    """Exception raised when a resource is not found."""
    pass

class ValidationException(ServiceException):
    """Exception raised when validation fails."""
    pass

class UnauthorizedException(ServiceException):
    """Exception raised when user is not authorized."""
    pass
