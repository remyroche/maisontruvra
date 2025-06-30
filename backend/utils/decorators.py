import logging
from typing import Callable, Any
from flask import jsonify, request, g, Response, abort, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt, jwt_required
from backend.models.user_models import User
from backend.services.audit_log_service import AuditLogService
from backend.utils.csrf_protection import CSRFProtection
from marshmallow import ValidationError
from ..models import User, AdminAuditLog, db

# Initialize loggers
logger = logging.getLogger(__name__)
security_logger = logging.getLogger('security')

class Permissions:
    """
    Defines constants for all permissions in the system to avoid magic strings.
    This provides a single source of truth for permission names.
    """
    # General Admin Access
    ADMIN_ACCESS = 'ADMIN_ACCESS'

    # User Management
    VIEW_USERS = 'VIEW_USERS'
    MANAGE_USERS = 'MANAGE_USERS'

    # B2B Management
    VIEW_B2B_ACCOUNTS = 'VIEW_B2B_ACCOUNTS'
    MANAGE_B2B_ACCOUNTS = 'MANAGE_B2B_ACCOUNTS'

    # Product Management
    VIEW_PRODUCTS = 'VIEW_PRODUCTS'
    MANAGE_PRODUCTS = 'MANAGE_PRODUCTS'
    
    # Order Management
    VIEW_ORDERS = 'VIEW_ORDERS'
    MANAGE_ORDERS = 'MANAGE_ORDERS'

    # Blog Management
    MANAGE_BLOG = 'MANAGE_BLOG'
    
    # Site Settings
    MANAGE_SITE_SETTINGS = 'MANAGE_SITE_SETTINGS'

    # Loyalty Program
    MANAGE_LOYALTY = 'MANAGE_LOYALTY'
    
    # Invoices & Quotes
    MANAGE_INVOICES = 'MANAGE_INVOICES'

    # View Audit Logs
    VIEW_AUDIT_LOGS = 'VIEW_AUDIT_LOGS'

    # All permissions grouped for convenience
    ALL = [
        ADMIN_ACCESS, VIEW_USERS, MANAGE_USERS, VIEW_B2B_ACCOUNTS,
        MANAGE_B2B_ACCOUNTS, VIEW_PRODUCTS, MANAGE_PRODUCTS, VIEW_ORDERS,
        MANAGE_ORDERS, MANAGE_BLOG, MANAGE_SITE_SETTINGS, MANAGE_LOYALTY,
        MANAGE_INVOICES, VIEW_AUDIT_LOGS
    ]

def require_b2b_user(f):
    """
    A decorator to ensure the current user is a logged-in B2B user.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in g or not g.user:
            abort(401, description="Authentication required.")
        if not hasattr(g.user, 'is_b2b') or not g.user.is_b2b:
            abort(403, description="Access denied. B2B account required.")
        return f(*args, **kwargs)
    return decorated_function

def require_b2c_user(f):
    """
    A decorator to ensure the current user is a logged-in B2C user.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in g or not g.user:
            abort(401, description="Authentication required.")
        if hasattr(g.user, 'is_b2b') and g.user.is_b2b:
            abort(403, description="Access denied. This area is for B2C users.")
        return f(*args, **kwargs)
    return decorated_function

def get_object_or_404(model):
    """
    A decorator to fetch a model instance by its ID from the route's URL variables.
    If the object is not found, it aborts the request with a 404 error.
    The fetched object is added to Flask's request context `g`.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            object_id_key = f"{model.__name__.lower()}_id"
            if object_id_key not in kwargs and 'id' in kwargs:
                object_id_key = 'id'

            if object_id_key not in kwargs:
                abort(500, description=f"Could not find ID key for model {model.__name__} in route.")

            obj_id = kwargs.get(object_id_key)
            obj = model.query.get(obj_id)
            
            if obj is None:
                abort(404, description=f"{model.__name__} with ID {obj_id} not found.")
            
            setattr(g, model.__name__.lower(), obj)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def api_resource_handler(model, schema=None, role_required=None, action_log=None, check_ownership=False):
    """
    A comprehensive decorator that handles role checks, object fetching,
    input validation, and activity logging for API resource routes.
    check_ownership: (Optional) Enforces that g.user.id matches the resource's user_id.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. Fetch the object (reusing get_object_or_404 logic)
            object_id_key = f"{model.__name__.lower()}_id"
            if object_id_key not in kwargs and 'id' in kwargs:
                object_id_key = 'id'

            target_object = None
            if object_id_key in kwargs:
                obj_id = kwargs.get(object_id_key)
                target_object = model.query.get(obj_id)
                if target_object is None:
                    abort(404, description=f"{model.__name__} with ID {obj_id} not found.")
                setattr(g, model.__name__.lower(), target_object)

            # 2. Ownership Check (only if requested)
            if check_ownership and target_object:
                if 'user' not in g or not g.user:
                    abort(401, description="Authentication required to check resource ownership.")
                if not hasattr(target_object, 'user_id') or target_object.user_id != g.user.id:
                    abort(403, description="You do not have permission to access this resource.")

            # 3. Input Validation (for POST/PUT)
            if request.method in ['POST', 'PUT']:
                if not schema:
                    abort(500, description="A schema must be provided for validation on POST/PUT requests.")
                try:
                    g.validated_data = schema.load(request.get_json())
                except ValidationError as err:
                    abort(400, description={"errors": err.messages})

            # Execute the actual route function
            response = f(*args, **kwargs)

            # 4. Activity Logging (if action_log is provided and user is authenticated)
            if action_log and (200 <= response.status_code < 300) and user:
                log_message = action_log
                # Allow for dynamic log messages
                if callable(action_log):
                    log_message = action_log(target_object)

                audit_log_service.log_activity(
                    user_id=user.id,
                    action=log_message,
                    target_id=target_object.id if target_object else None,
                    target_type=model.__name__ if target_object else None
                )

            return response
        return decorated_function
    return decorator
    
    
def _execute_and_log_action(func: Callable, *args: Any, **kwargs: Any) -> Any:
    """
    Private helper to execute the decorated staff/admin route function and log the action.
    This should only be called AFTER a permission check has passed.
    """
    user = getattr(g, 'user', None)
    if not user:
        return func(*args, **kwargs)

    try:
        response = func(*args, **kwargs)
        
        status_code = 200
        if isinstance(response, tuple): # e.g., (jsonify(...), 201)
            status_code = response[1]
        elif isinstance(response, Response):
            status_code = response.status_code
        
        is_success = 200 <= status_code < 400
        
        details = f"Endpoint: {request.path}, Method: {request.method}, Status: {status_code}"
        AuditLogService.log_action(
            user_id=user.id,
            action=func.__name__,
            details=details,
            success=is_success
        )
        return response
    except Exception as e:
        logger.error(f"Exception in admin action {func.__name__}: {e}", exc_info=True)
        AuditLogService.log_action(
            user_id=user.id,
            action=func.__name__,
            details=f"Endpoint: {request.path} failed with Exception: {str(e)}",
            success=False
        )
        raise e

def _common_auth_check() -> Response | None:
    """
    Performs common authentication and user status checks.
    Populates g.user with the User object.
    """
    user_id = get_jwt_identity()
    if not user_id:
        security_logger.warning({
            'message': 'Unauthenticated access attempt',
            'endpoint': request.path,
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'referrer': request.headers.get('Referer')
        })
        return jsonify(status="error", message="Authentication required."), 401

    user_obj = User.query.get(user_id)
    if not user_obj:
        security_logger.warning({
            'message': 'User ID from JWT not found in DB',
            'userId': user_id,
            'endpoint': request.path,
            'ip': request.remote_addr
        })
        return jsonify(status="error", message="User not found."), 401

    if not user_obj.is_active:
        security_logger.warning({
            'message': 'Inactive user access attempt',
            'userId': user_id,
            'endpoint': request.path
        })
        return jsonify(status="error", message="Account is inactive."), 401

    g.user = user_obj
    return None

def _csrf_check() -> Response | None:
    """Validates CSRF token for state-changing requests."""
    if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
        try:
            CSRFProtection.validate_csrf_token()
        except Exception as e:
            security_logger.warning({
                'message': 'CSRF validation failed',
                'userId': g.user.id,
                'endpoint': request.path,
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'error': str(e)
            })
            return jsonify(status="error", message="CSRF validation failed"), 403
    return None

def _apply_base_security_checks(f: Callable) -> Callable:
    """
    A core decorator that applies JWT, user loading, and CSRF checks.
    This is the foundation for all other authentication decorators.
    """
    @wraps(f)
    @jwt_required()
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        auth_error = _common_auth_check()
        if auth_error:
            return auth_error

        csrf_error = _csrf_check()
        if csrf_error:
            return csrf_error
            
        return f(*args, **kwargs)
    return wrapper

def login_required(f: Callable) -> Callable:
    """
    A general-purpose decorator to ensure a user is logged in and active.
    It applies all base security checks.
    """
    @wraps(f)
    @_apply_base_security_checks
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        return f(*args, **kwargs)
    return decorated_function

def b2b_user_required(f: Callable) -> Callable:
    """
    Checks if a logged-in user has B2B privileges. This decorator handles
    all authentication and B2B status checks in one.
    """
    @wraps(f)
    @login_required # This now handles auth, user loading, and CSRF checks.
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        # g.user is guaranteed to exist here because of @login_required.
        claims = get_jwt()
        if not claims.get('is_b2b_user', False) or not g.user.is_b2b:
            security_logger.warning(f"B2B access denied for user {g.user.email} at {request.path}.")
            return jsonify(error="B2B professional account required."), 403
        
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f: Callable) -> Callable:
    """
    Checks if the user has staff privileges. Admins are implicitly staff.
    Logs the action upon successful execution.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not g.user.is_staff and not g.user.is_admin:
            AuditLogService.log_action(
                user_id=g.user.id,
                action=f"FAILED_STAFF_ACCESS: {f.__name__}",
                details=f"User '{g.user.email}' lacks staff privileges for {request.path}.",
                success=False
            )
            return jsonify(error="Staff access required"), 403
        return _execute_and_log_action(f, *args, **kwargs)
    return decorated_function

def admin_required(f: Callable) -> Callable:
    """
    Checks if the user is an admin. The ultimate permission.
    Logs the action upon successful execution.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not g.user.is_admin:
            AuditLogService.log_action(
                user_id=g.user.id,
                action=f"FAILED_ADMIN_ACCESS: {f.__name__}",
                details=f"User '{g.user.email}' is not an admin for endpoint {request.path}.",
                success=False
            )
            return jsonify(error="Administrator access required"), 403
        return _execute_and_log_action(f, *args, **kwargs)
    return decorated_function

def roles_required(*roles: str) -> Callable:
    """
    Generic decorator to check for specific roles. Admins implicitly pass.
    Logs the action upon successful execution.
    """
    def wrapper(f: Callable) -> Callable:
        @wraps(f)
        @login_required
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            if g.user.is_admin:
                return _execute_and_log_action(f, *args, **kwargs)
            
            user_roles = {role.name for role in g.user.roles}
            if not user_roles.intersection(roles):
                AuditLogService.log_action(
                    user_id=g.user.id,
                    action=f"FAILED_ROLE_ACCESS: {f.__name__}",
                    details=f"User '{g.user.email}' lacks required roles {list(roles)} for {request.path}.",
                    success=False
                )
                return jsonify(error="Insufficient role permissions"), 403
            return _execute_and_log_action(f, *args, **kwargs)
        return decorated_function
    return wrapper

def permissions_required(*permission_names: str) -> Callable:
    """
    Ensures the user has ALL of the specified permissions. Admins always pass.
    Logs the action upon successful execution.
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        @login_required
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            if g.user.is_admin:
                return _execute_and_log_action(f, *args, **kwargs)

            user_permissions = g.user.get_permissions()
            if not set(permission_names).issubset(user_permissions):
                missing_perms = set(permission_names) - user_permissions
                AuditLogService.log_action(
                    user_id=g.user.id,
                    action=f"FAILED_PERMISSION_ACCESS: {f.__name__}",
                    details=f"User '{g.user.email}' lacks permissions: {list(missing_perms)} for {request.path}.",
                    success=False
                )
                return jsonify({"error": f"Requires permissions: {', '.join(missing_perms)}"}), 403
            return _execute_and_log_action(f, *args, **kwargs)
        return decorated_function
    return decorator

def b2b_admin_required(f: Callable) -> Callable:
    """
    Checks if a user is an admin within their B2B company.
    A user is a B2B admin if they are a B2B user and either:
    1. Are a site-wide admin.
    2. Have the 'B2B Admin' role.
    Requires a fresh JWT and logs the action.
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        # Check if user is a B2B user
        claims = get_jwt()
        if not claims.get('is_b2b_user', False) or not g.user.is_b2b:
            security_logger.warning(f"B2B Admin access denied for non-B2B user {g.user.email} at {request.path}.")
            return jsonify(error="B2B professional account required."), 403

        user_roles = {role.name for role in g.user.roles}
        if 'B2B Admin' not in user_roles:
            AuditLogService.log_action(
                user_id=g.user.id,
                action=f"FAILED_B2B_ADMIN_ACCESS: {f.__name__}",
                details=f"User '{g.user.email}' lacks 'B2B Admin' role for {request.path}.",
                success=False
            )
            return jsonify(error="B2B administrator privileges required."), 403
            
        return _execute_and_log_action(f, *args, **kwargs)
    return decorated_function


def log_admin_action(f: Callable) -> Callable:
    """
    DEPRECATED: This decorator is no longer needed. Action logging is now built
    into the permission/role decorators themselves (`admin_required`, `staff_required`, etc.).
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        logger.warning("The @log_admin_action decorator is deprecated and can be removed.")
        return _execute_and_log_action(f, *args, **kwargs)
    return decorated_function
