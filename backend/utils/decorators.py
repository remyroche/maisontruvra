from functools import wraps
from flask import jsonify, request
from flask_login import current_user
from backend.services.audit_log_service import AuditLogService
import re
from functools import wraps
from flask import request, g, abort
from backend.services.audit_log_service import create_audit_log
from backend.models.user_models import User # Assuming User model is here for role checks

def _execute_and_log_action(func, *args, **kwargs):
    """
    Private helper function to execute the decorated route function and log the 
    action to the audit trail. This should only be called AFTER a permission 
    check has passed.
    """
    # Check if a user is available in the global context
    if not hasattr(g, 'user') or not g.user:
        # This case should ideally not be hit if used with an auth decorator,
        # but it's a safe fallback.
        return func(*args, **kwargs)

    try:
        # Execute the original function (the admin route)
        response = func(*args, **kwargs)
        
        # Determine success and status code from the response
        is_success = True
        status_code = 200 # Default success
        if hasattr(response, 'status_code'):
             is_success = 200 <= response.status_code < 400
             status_code = response.status_code

        details = f"Endpoint: {request.path}, Method: {request.method}, Status: {status_code}"
        
        create_audit_log(
            user_id=g.user.id,
            action=func.__name__, # Log using the function's name
            details=details,
            success=is_success
        )
        return response
    except Exception as e:
        # Log the exception as a failed action
        create_audit_log(
            user_id=g.user.id,
            action=func.__name__,
            details=f"Endpoint: {request.path} failed with Exception: {str(e)}",
            success=False
        )
        # Re-raise the exception to be handled by Flask's error handlers
        raise e

def login_required(f):
    """Checks if a user is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'user') or not g.user:
            abort(401) # Unauthorized
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Checks if the user is an admin. If so, executes and logs the action.
    Also logs failed authorization attempts.
    """
    @wraps(f)
    @login_required # Ensure user is logged in first
    def decorated_function(*args, **kwargs):
        if not g.user.is_admin:
            # Log the authorization failure
            create_audit_log(
                user_id=g.user.id,
                action=f.__name__,
                details=f"Authorization failed: User '{g.user.email}' is not an admin for endpoint {request.path}.",
                success=False
            )
            abort(403) # Forbidden
        
        # If authorized, execute the action and log it
        return _execute_and_log_action(f, *args, **kwargs)
    return decorated_function

def staff_required(f):
    """
    Checks if the user has staff privileges (is_staff or is_admin). 
    If so, executes and logs the action.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # Admins are implicitly considered staff
        if not g.user.is_staff and not g.user.is_admin:
            create_audit_log(
                user_id=g.user.id,
                action=f.__name__,
                details=f"Authorization failed: User '{g.user.email}' lacks staff privileges for endpoint {request.path}.",
                success=False
            )
            abort(403) # Forbidden
        return _execute_and_log_action(f, *args, **kwargs)
    return decorated_function

def roles_required(*roles):
    """
    Generic decorator to check for specific roles.
    Executes and logs the action if the user has any of the required roles.
    """
    def wrapper(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            # Assumes user model has a `roles` relationship that returns a list of Role objects
            user_roles = {role.name for role in g.user.roles}
            if not user_roles.intersection(roles):
                create_audit_log(
                    user_id=g.user.id,
                    action=f.__name__,
                    details=f"Authorization failed: User '{g.user.email}' lacks required roles {list(roles)} for endpoint {request.path}.",
                    success=False
                )
                abort(403) # Forbidden
            return _execute_and_log_action(f, *args, **kwargs)
        return decorated_function
    return wrapper

def permissions_required(*permission_names):
    """Ensures the user has ALL of the specified permissions. Admins always pass."""
    def decorator(f):
        @wraps(f)
        @staff_required # All permission-based routes are for staff
        def decorated_function(*args, **kwargs):
            if current_user.is_admin:
                return f(*args, **kwargs)

            user_permissions = current_user.get_permissions()
            if not set(permission_names).issubset(user_permissions):
                return jsonify({"error": f"Requires all of the following permissions: {', '.join(permission_names)}"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def _generate_action_name(func_name):
    """Transforms a function name like 'soft_delete_user' into 'Soft Delete User'."""
    return ' '.join(word.capitalize() for word in func_name.split('_'))

def audit_action(f):
    """
    Decorator to automatically log a staff action to the audit log.
    It inspects the request and function name to create a meaningful log message.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Execute the function first to see if it succeeds
        response_tuple = f(*args, **kwargs)
        
        # Flask returns a tuple (response, status_code) or a Response object
        if isinstance(response_tuple, tuple):
            response, status_code = response_tuple
        else:
            response = response_tuple
            status_code = response.status_code

        # Only log successful actions (2xx status codes)
        if 200 <= status_code < 300:
            action_name = _generate_action_name(f.__name__)
            details = f"Route: {request.path} | Method: {request.method}"
            
            payload = request.get_json(silent=True)
            if payload:
                # Avoid logging sensitive info like passwords
                sensitive_keys = ['password', 'token', 'secret']
                filtered_payload = {k: v for k, v in payload.items() if k not in sensitive_keys}
                details += f" | Payload: {filtered_payload}"
            
            AuditLogService.create_log(
                staff_user_id=current_user.id,
                action=action_name,
                details=details
            )
        return response, status_code
    return decorated_function

# Alias for backward compatibility
log_admin_action = audit_action

