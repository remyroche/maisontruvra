from functools import wraps
from flask import jsonify
from flask_login import current_user
from backend.services.audit_log_service import AuditLogService

def admin_required(f):
    """Ensures the user is authenticated and is an admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*role_names):
    """
    Ensures the user has at least one of the specified roles.
    Falls back to admin_required if no roles are provided.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"error": "Authentication required"}), 401
            
            # Admins have access to everything
            if current_user.is_admin:
                return f(*args, **kwargs)

            user_roles = {role.name for role in current_user.roles}
            if not set(role_names).intersection(user_roles):
                return jsonify({"error": f"Requires one of the following roles: {', '.join(role_names)}"}), 403
            return f(*args, **kwargs)
        return decorated_function
    # If called as @roles_required with no roles, it's a mistake. Default to admin.
    if not role_names:
        return admin_required
    return decorator


def permissions_required(*permission_names):
    """
    Ensures the user has ALL of the specified permissions.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                 return jsonify({"error": "Authentication required"}), 401
            
            if current_user.is_admin:
                return f(*args, **kwargs)

            user_permissions = current_user.get_permissions()
            if not set(permission_names).issubset(user_permissions):
                return jsonify({"error": f"Requires all of the following permissions: {', '.join(permission_names)}"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def audit_admin_action(action_name):
    """
    Decorator to automatically log an admin action to the audit log.
    It inspects the request to create a meaningful log message.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Execute the function first to see if it succeeds
            response = f(*args, **kwargs)
            
            # Only log successful actions (2xx status codes)
            if 200 <= response.status_code < 300:
                details = f"Route: {request.path} | Method: {request.method}"
                # Add request data to details if available
                if request.is_json and request.get_json():
                    details += f" | Payload: {request.get_json()}"
                
                AuditLogService.create_log(
                    admin_user_id=current_user.id,
                    action=action_name,
                    details=details
                )
            return response
        return decorated_function
    return decorator
