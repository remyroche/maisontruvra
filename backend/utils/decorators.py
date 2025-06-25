from functools import wraps
from flask import jsonify, request
from flask_login import current_user
from backend.services.audit_log_service import AuditLogService
import re

def staff_required(f):
    """Ensures the user is an authenticated staff member (not B2C or B2B)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_staff:
            return jsonify({"error": "Staff access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*role_names):
    """Ensures the user has at least one of the specified roles. Admins always pass."""
    def decorator(f):
        @wraps(f)
        @staff_required # All role-based routes are for staff
        def decorated_function(*args, **kwargs):
            if current_user.is_admin:
                return f(*args, **kwargs)

            user_roles = {role.name for role in current_user.roles}
            if not set(role_names).intersection(user_roles):
                return jsonify({"error": f"Requires one of the following roles: {', '.join(role_names)}"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

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
