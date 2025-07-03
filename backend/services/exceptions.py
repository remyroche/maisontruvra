# backend/services/exceptions.py

# ==============================================================================
# Base Exception
# ==============================================================================

class ServiceException(Exception):
    """
    The base exception class for all custom service-layer errors.
    All other service exceptions should inherit from this class.
    """
    status_code = 500
    message = "An internal service error occurred."

    def __init__(self, message=None, status_code=None, payload=None):
        super().__init__()
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """Converts the exception into a dictionary for API responses."""
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

# ==============================================================================
# 5xx Server-Side and External Errors
# ==============================================================================

class ServiceError(ServiceException):
    """
    A generic error for failed service operations. (HTTP 500)
    This is the catch-all for unexpected internal errors.
    """
    status_code = 500
    message = "An unexpected error occurred in the service."


class ExternalServiceException(ServiceException):
    """
    Raised when an external API or service fails (e.g., payment gateway, email provider). (HTTP 503)
    """
    status_code = 503
    message = "An error occurred with an external service."

# ==============================================================================
# 4xx Client-Side Errors
# ==============================================================================

class ValidationException(ServiceException):
    """
    Raised when incoming data fails validation checks. (HTTP 400)
    """
    status_code = 400
    message = "One or more validation errors occurred."

class UpdateException(ServiceException):
    """
    Raised when an update operation fails for reasons other than validation. (HTTP 400)
    """
    status_code = 400
    message = "Failed to update the resource."


class DeletionException(ServiceException):
    """
    Raised when a delete operation fails, often due to business rules. (HTTP 400)
    """
    status_code = 400
    message = "Failed to delete the resource."

class BusinessRuleException(ValidationException):
    """
    Raised when an action violates a specific business rule (e.g., applying an expired discount). (HTTP 400)
    """
    message = "The requested action violates a business rule."
class ReferralException(BusinessRuleException):
    """
    Raised for referral-specific business rule violations. (HTTP 400)
    """
    message = "A referral error occurred."


class InsufficientStockError(BusinessRuleException):
    """
    Raised when there is not enough stock to fulfill a request. (HTTP 400)
    """
    message = "Insufficient stock for the requested item."

class InvalidAPIRequestError(ValidationException):
    """Raised for malformed or invalid API requests."""
    message = "The API request is invalid or missing required parameters."

class DataConflictException(ValidationException):
    """
    Raised when trying to create a resource that already exists (e.g., duplicate email). (HTTP 409)
    """
    status_code = 409
    message = "A resource with the provided data already exists."
class DuplicateProductError(DataConflictException):
    """Raised when trying to create a product that already exists (e.g., duplicate SKU)."""
    message = "A product with this SKU or name already exists."
class NotFoundException(ServiceException):
    """
    Raised when a specific resource cannot be found in the database. (HTTP 404)
    """
    status_code = 404
    message = "The requested resource was not found."

    def __init__(self, resource_name="Resource", resource_id=None, **kwargs):
        message = f"The requested {resource_name.lower()} was not found."
        if resource_id:
            message = f"{resource_name.capitalize()} with ID '{resource_id}' was not found."
        super().__init__(message=message, **kwargs)


class ProductNotFoundError(NotFoundException):
    """
    Raised specifically when a product cannot be found. (HTTP 404)
    """
    def __init__(self, product_id=None):
        super().__init__(resource_name="product", resource_id=product_id)


class UserNotFoundException(NotFoundException):
    """
    Raised specifically when a user cannot be found. (HTTP 404)
    """
    def __init__(self, user_id=None):
        super().__init__(resource_name="user", resource_id=user_id)

class AuthenticationException(ServiceException):
    """
    Raised for authentication failures (e.g., invalid credentials, bad token). (HTTP 401)
    """
    status_code = 401
    message = "Authentication failed."

class AuthorizationException(ServiceException):
    """
    Raised when an authenticated user is not permitted to perform an action. (HTTP 403)
    """
    status_code = 403
    message = "You are not authorized to perform this action."

    # --- Authentication and Authorization Errors ---

class UnauthorizedException(ServiceException):
    """
    Raised when authentication is required and has failed or has not yet been provided. (HTTP 401 Unauthorized)
    This is the general exception for "login required".
    """
    status_code = 401
    message = "Authentication is required to access this resource."

class AuthenticationException(UnauthorizedException):
    """
    A more specific version of UnauthorizedException, often used for invalid credentials during a login attempt. (HTTP 401)
    """
    message = "Authentication failed due to invalid credentials."


class InvalidPasswordException(AuthenticationException):
    """
    Raised specifically when a password does not match during an authentication attempt. (HTTP 401)
    """
    message = "The password provided is incorrect."


class InvalidCredentialsError(AuthenticationException):
    """
    Raised specifically for a bad username/password combination. (HTTP 401)
    """
    message = "Invalid email or password."

class AuthorizationException(ServiceException):
    """
    Raised when an authenticated user is not permitted to perform a specific action. (HTTP 403 Forbidden)
    Use this when the user is logged in, but lacks the necessary permissions.
    """
    status_code = 403
    message = "You are not authorized to perform this action."