from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from backend.services.rbac_service import RBACService

def permission_required(*permissions):
    """
    A decorator to protect routes that require specific permissions.
    Checks if the user has ALL of the given permissions.
    e.g. @permission_required('MANAGE_USERS', 'VIEW_AUDIT_LOG')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            # This method needs to be implemented in RBACService.
            # It should check if the user's roles grant them all the required permissions.
            if not RBACService.user_has_permissions(user_id, *permissions):
                perms_str = ", ".join(permissions)
                return jsonify(msg=f"Insufficient permissions. Requires: {perms_str}"), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def admin_required(fn):
    """
    A decorator to protect routes that require admin privileges.
    This is now a specific check to see if the user has the 'Admin' role,
    which is assumed to have super-user privileges and is managed separately.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        # This method needs to be implemented in RBACService.
        if not RBACService.user_has_role(user_id, 'Admin'):
            return jsonify(msg="Admins only!"), 403
        else:
            return fn(*args, **kwargs)
    return wrapper

def b2b_user_required(fn):
    """
    A decorator to protect routes that require a logged-in B2B user.
    Checks if the user has the 'B2B' role.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        # This method needs to be implemented in RBACService.
        if not RBACService.user_has_role(user_id, 'B2B'):
            return jsonify(msg="B2B account required."), 403
        else:
            return fn(*args, **kwargs)
    return wrapper