from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from backend.services.rbac_service import RBACService

from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from backend.services.rbac_service import RBACService # Assume this exists

def staff_required(fn):
    """
    A decorator to protect routes that require staff privileges.
    It checks for two things:
    1. The user has a role considered to be 'staff'.
    2. If the user has MFA enabled, their session JWT must contain the
       'mfa_verified' claim, proving they passed the second factor check.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        # 1. Check if the user has a staff role using the RBAC service.
        # This is more flexible than checking for a single 'Admin' role.
        if not RBACService.user_is_staff(user_id):
            return jsonify(msg="Staff account required."), 403

        # 2. Check the user's MFA status from the database.
        # In a real app, this could be cached to avoid DB hits on every request.
        user = User.get_by_id(user_id) # Assumed method
        if user and user.is_mfa_enabled:
            # If MFA is enabled for this user, their token MUST have the
            # 'mfa_verified' claim.
            claims = get_jwt()
            if not claims.get("mfa_verified"):
                return jsonify(msg="MFA verification is required for this action."), 403
        
        # If all checks pass, proceed to the route handler.
        return fn(*args, **kwargs)
    return wrapper
    
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
