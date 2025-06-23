from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from backend.services.rbac_service import RBACService
# In a real implementation, you would have access to the User model, for now we assume
# RBACService can handle the necessary checks.
# from backend.models.user_models import User

def permissions_required(*required_permissions):
    """
    Decorator that checks if a user has EITHER the 'Admin' role OR
    ALL of the specified permissions.

    This acts as a single, clean authorization check, fulfilling the need for
    an 'Admin fallback' without stacking multiple decorators. It improves on
    the original by centralizing the logic.

    Usage:
    @permissions_required('MANAGE_PRODUCTS', 'VIEW_INVENTORY')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()

                if not user_id:
                    return jsonify(status="error", message="Authentication required."), 401

                # 1. Admin fallback: If the user is an Admin, grant access immediately.
                if RBACService.user_has_role(user_id, 'Admin'):
                    return fn(*args, **kwargs)

                # 2. Permission check: If not an admin, check for all required permissions.
                if not RBACService.user_has_permissions(user_id, *required_permissions):
                    perms_str = ", ".join(required_permissions)
                    return jsonify(status="error", message=f"Insufficient permissions. Requires: {perms_str} or Admin role."), 403

                return fn(*args, **kwargs)
            except Exception as e:
                # Log the exception e
                return jsonify(status="error", message="An error occurred during permission check."), 500
        return wrapper
    return decorator

def admin_required(fn):
    """
    A decorator to protect routes that require the 'Admin' role specifically.
    This is intended for actions that ONLY an admin should perform, without fallbacks.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify(status="error", message="Authentication required."), 401
        if not RBACService.user_has_role(user_id, 'Admin'):
            return jsonify(status="error", message="Administrator access required."), 403
        return fn(*args, **kwargs)
    return wrapper

def staff_required(fn):
    """
    A decorator to protect routes that require staff privileges.
    It checks for a staff role and, if MFA is enabled for that user,
    ensures the JWT indicates that MFA has been verified.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()

        if not user_id:
            return jsonify(status="error", message="Authentication required."), 401

        # Check if the user has a staff role via the RBAC service.
        if not RBACService.user_is_staff(user_id):
            return jsonify(status="error", message="Staff account required."), 403

        # This assumes the login flow adds an 'mfa_verified' claim to the JWT
        # if the user has MFA enabled and has successfully passed the second factor.
        # A more robust implementation might re-verify with the database in some cases.
        claims = get_jwt()
        if claims.get("mfa_required") and not claims.get("mfa_verified"):
            return jsonify(status="error", message="Multi-Factor Authentication is required for this action."), 403

        return fn(*args, **kwargs)
    return wrapper

def b2b_user_required(fn):
    """
    A decorator to protect routes that require a logged-in B2B user.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify(status="error", message="Authentication required."), 401
        if not RBACService.user_has_role(user_id, 'B2B'):
            return jsonify(status="error", message="B2B account required."), 403
        return fn(*args, **kwargs)
    return wrapper

