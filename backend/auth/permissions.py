from functools import wraps
from flask import jsonify, request, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt, jwt_required
import logging

from backend.services.rbac_service import rbac_service as RBACService
from backend.utils.csrf_protection import CSRFProtection
from backend.models.user_models import User

logger = logging.getLogger(__name__)
security_logger = logging.getLogger('security')

# RBACService is imported from backend.services.rbac_service

# CSRFProtection is imported from backend.utils.csrf_protection

# User model is imported from backend.models.user_models


def _common_auth_check(fn, user_id):
    """
    Helper function to perform common authentication and user status checks.
    Populates g.user with a dictionary representation of the user.
    """
    if not user_id:
        security_logger.warning({
            'message': 'Unauthenticated access attempt',
            'endpoint': request.path,
            'ip': request.remote_addr,
            'request_id': getattr(g, 'request_id', 'unknown')
        })
        return jsonify(status="error", message="Authentication required."), 401

    user_obj = User.query.get(user_id)
    if not user_obj:
        security_logger.warning({
            'message': 'User ID from JWT not found in DB',
            'userId': user_id,
            'endpoint': request.path,
            'ip': request.remote_addr,
            'request_id': getattr(g, 'request_id', 'unknown')
        })
        return jsonify(status="error", message="User not found."), 401

    if not user_obj.is_active:
        security_logger.warning({
            'message': 'Inactive user access attempt',
            'userId': user_id,
            'endpoint': request.path,
            'ip': request.remote_addr,
            'request_id': getattr(g, 'request_id', 'unknown')
        })
        return jsonify(status="error", message="Account inactive."), 401

    # Store relevant user info in g for use in the route and subsequent checks
    # Get user role - handle different possible role structures
    user_role = 'Customer'  # default role
    if hasattr(user_obj, 'roles') and user_obj.roles:
        user_role = user_obj.roles[0].name if user_obj.roles else 'Customer'
    elif hasattr(user_obj, 'role') and user_obj.role:
        user_role = user_obj.role.name if hasattr(user_obj.role, 'name') else str(user_obj.role)
    
    # Get MFA status
    mfa_enabled = getattr(user_obj, 'two_factor_enabled', False) or getattr(user_obj, 'mfa_enabled', False)
    
    g.user = {
        'id': user_obj.id,
        'email': user_obj.email,
        'role': user_role,
        'two_factor_enabled': mfa_enabled
    }
    security_logger.debug(f"User {user_id} authenticated and active. Role: {user_role}, MFA Enabled: {mfa_enabled}")
    return None

def _csrf_and_state_change_check(fn):
    """
    Helper function to validate CSRF token for state-changing requests.
    Assumes g.user is already populated by a prior check.
    """
    if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
        try:
            CSRFProtection.validate_csrf_token()
            security_logger.info({
                'message': 'CSRF token validated',
                'userId': g.user['id'],
                'endpoint': request.path,
                'method': request.method,
                'request_id': getattr(g, 'request_id', 'unknown')
            })
        except Exception as e:
            security_logger.warning({
                'message': 'CSRF validation failed',
                'userId': g.user['id'],
                'endpoint': request.path,
                'method': request.method,
                'error': str(e),
                'request_id': getattr(g, 'request_id', 'unknown')
            })
            return jsonify(status="error", message="CSRF validation failed"), 403
    return None

def _apply_base_security_checks(fn):
    """
    A helper decorator that performs common authentication, CSRF,
    and mandatory MFA checks (if MFA is enabled for the user's account and session not verified).
    This decorator assumes @jwt_required() has already run.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity() # Should be available as jwt_required has run

        # Perform common authentication and user status check
        error_response = _common_auth_check(fn, user_id)
        if error_response:
            return error_response

        # Perform CSRF protection for state-changing methods
        error_response = _csrf_and_state_change_check(fn)
        if error_response:
            return error_response

        # --- MFA Access Control Logic ---
        user_info = g.user # Access the user info dictionary populated by _common_auth_check
        current_path = request.path

        # Define paths that are exceptions to the strict MFA requirement
        # These are pages where a privileged user can go EVEN IF their MFA is not verified yet
        MFA_EXEMPT_PATHS = [
            '/admin/setup-mfa', # Page to set up or verify MFA
            '/admin/login',     # Re-login page if session expired or MFA is pending
        ]

        # Determine if the user is a privileged user (Admin or Staff)
        is_privileged_user = user_info.get('role') in ['Admin', 'Staff']

        # If the user is privileged, enforce MFA compliance
        if is_privileged_user:
            claims = get_jwt() # Get current JWT claims
            
            # MFA is *not* compliant if:
            # 1. user_info.get('two_factor_enabled', False) is False (MFA not enabled on account)
            # OR
            # 2. claims.get("mfa_verified", False) is False (MFA enabled but not verified in current session)
            mfa_is_not_compliant = not user_info.get('two_factor_enabled', False) or \
                                   not claims.get("mfa_verified", False)

            if mfa_is_not_compliant:
                # If the current request path is NOT one of the MFA exempt paths, then deny access
                if current_path not in MFA_EXEMPT_PATHS:
                    security_logger.warning({
                        'message': 'Privileged user access denied: MFA not enabled or not verified.',
                        'userId': user_info['id'],
                        'endpoint': current_path,
                        'reason': 'MFA not compliant',
                        'ip': request.remote_addr,
                        'request_id': getattr(g, 'request_id', 'unknown')
                    })
                    return jsonify(status="error", message="Multi-Factor Authentication is mandatory for privileged access. Please set up and verify MFA."), 403
                # Else (it is an exempt path), allow the request to proceed
                security_logger.info(f"User {user_info['id']} (MFA not compliant) allowed access to MFA exempt path: {current_path}")
        # --- End of MFA Access Control Logic ---

        # If all common security checks pass, execute the original function
        return fn(*args, **kwargs)
    return wrapper


def permissions_required(*required_permissions):
    """
    Decorator that checks if a user has EITHER the 'Admin' role OR
    ALL of the specified permissions, and passes common security checks including MFA if enabled.
    """
    def decorator(fn):
        @wraps(fn)
        @jwt_required() # Ensure JWT is present and valid
        @_apply_base_security_checks # Apply the common security checks
        def wrapper(*args, **kwargs):
            try:
                user_id = get_jwt_identity() # User ID and g.user is now guaranteed to be populated and active

                # 1. Admin fallback: If the user is an Admin, grant access immediately.
                if RBACService.user_has_role(user_id, 'Admin'):
                    security_logger.info(f"User {user_id} (Admin) granted access to {request.path}")
                    return fn(*args, **kwargs)

                # 2. Permission check: If not an admin, check for all required permissions.
                if not RBACService.user_has_permissions(user_id, *required_permissions):
                    perms_str = ", ".join(required_permissions)
                    security_logger.warning({
                        'message': 'Insufficient permissions',
                        'userId': user_id,
                        'requiredPermissions': list(required_permissions),
                        'endpoint': request.path,
                        'ip': request.remote_addr,
                        'request_id': getattr(g, 'request_id', 'unknown')
                    })
                    return jsonify(status="error", message=f"Insufficient permissions. Requires: {perms_str} or Admin role."), 403

                security_logger.info(f"User {user_id} granted access with permissions {required_permissions} to {request.path}")
                return fn(*args, **kwargs)
            except Exception as e:
                security_logger.error(f"Unhandled error in permissions_required for {request.path}: {e}", exc_info=True)
                return jsonify(status="error", message="An internal server error occurred during permission check."), 500
        return wrapper
    return decorator

def admin_required(fn):
    """
    A decorator to protect routes that require the 'Admin' role specifically,
    and passes common security checks including MFA if enabled.
    """
    @wraps(fn)
    @jwt_required() # Ensure JWT is present and valid
    @_apply_base_security_checks # Apply the common security checks
    def wrapper(*args, **kwargs):
        try:
            user_id = get_jwt_identity() # User ID and g.user is now guaranteed to be populated and active

            if not RBACService.user_has_role(user_id, 'Admin'):
                security_logger.warning({
                    'message': 'Admin access denied',
                    'userId': user_id,
                    'endpoint': request.path,
                    'ip': request.remote_addr,
                    'request_id': getattr(g, 'request_id', 'unknown')
                })
                return jsonify(status="error", message="Administrator access required."), 403

            security_logger.info(f"User {user_id} (Admin) granted access to {request.path}")
            return fn(*args, **kwargs)
        except Exception as e:
            security_logger.error(f"Unhandled error in admin_required for {request.path}: {e}", exc_info=True)
            return jsonify(status="error", message="An internal server error occurred during admin check."), 500
    return wrapper

def staff_required(fn):
    """
    A decorator to protect routes that require staff privileges,
    and passes common security checks including MFA if enabled.
    """
    @wraps(fn)
    @jwt_required() # Ensure JWT is present and valid
    @_apply_base_security_checks # Apply the common security checks
    def wrapper(*args, **kwargs):
        try:
            user_id = get_jwt_identity() # User ID and g.user is now guaranteed to be populated and active

            # Check if the user has a staff role via the RBAC service.
            if not RBACService.user_is_staff(user_id):
                security_logger.warning({
                    'message': 'Staff access denied',
                    'userId': user_id,
                    'endpoint': request.path,
                    'ip': request.remote_addr,
                    'request_id': getattr(g, 'request_id', 'unknown')
                })
                return jsonify(status="error", message="Staff account required."), 403

            security_logger.info(f"User {user_id} (Staff) granted access to {request.path}")
            return fn(*args, **kwargs)
        except Exception as e:
            security_logger.error(f"Unhandled error in staff_required for {request.path}: {e}", exc_info=True)
            return jsonify(status="error", message="An internal server error occurred during staff check."), 500
    return wrapper

def roles_required(*required_roles):
    """
    Decorator that checks if a user has at least ONE of the specified roles,
    and passes common security checks including MFA if enabled.
    """
    def decorator(fn):
        @wraps(fn)
        @jwt_required() # Ensure JWT is present and valid
        @_apply_base_security_checks # Apply the common security checks
        def wrapper(*args, **kwargs):
            try:
                user_id = get_jwt_identity() # User ID and g.user is now guaranteed to be populated and active

                user_roles = RBACService.get_user_roles(user_id)

                # Check if the user has any of the required roles
                has_required_role = any(role in user_roles for role in required_roles)

                if not has_required_role:
                    roles_str = ", ".join(required_roles)
                    security_logger.warning({
                        'message': 'Role access denied',
                        'userId': user_id,
                        'requiredRoles': list(required_roles),
                        'userRoles': user_roles,
                        'endpoint': request.path,
                        'ip': request.remote_addr,
                        'request_id': getattr(g, 'request_id', 'unknown')
                    })
                    return jsonify(status="error", message=f"Access denied. One of these roles is required: {roles_str}."), 403

                security_logger.info(f"User {user_id} granted access with roles {user_roles} to {request.path}")
                return fn(*args, **kwargs)
            except Exception as e:
                security_logger.error(f"Unhandled error in roles_required for {request.path}: {e}", exc_info=True)
                return jsonify(status="error", message="An internal server error occurred during role check."), 500
        return wrapper
    return decorator


def b2b_user_required(fn):
    """
    A decorator to protect routes that require a logged-in B2B user.
    Passes common security checks. No explicit MFA check here as it's not mandated for B2B users
    unless they also fall under a role/permission that does mandate it, which would be covered
    by other decorators.
    """
    @wraps(fn)
    @jwt_required() # Ensure JWT is present and valid
    @_apply_base_security_checks # Apply the common security checks
    def wrapper(*args, **kwargs):
        try:
            user_id = get_jwt_identity() # User ID and g.user is now guaranteed to be populated and active

            # Explicit B2B role check
            if not RBACService.user_has_role(user_id, 'B2B'):
                security_logger.warning({
                    'message': 'B2B user access denied',
                    'userId': user_id,
                    'endpoint': request.path,
                    'ip': request.remote_addr,
                    'request_id': getattr(g, 'request_id', 'unknown')
                })
                return jsonify(status="error", message="B2B account required."), 403

            security_logger.info(f"User {user_id} (B2B) granted access to {request.path}")
            return fn(*args, **kwargs)
        except Exception as e:
            security_logger.error(f"Unhandled error in b2b_user_required for {request.path}: {e}", exc_info=True)
            return jsonify(status="error", message="An internal server error occurred during B2B user check."), 500
    return wrapper


def rbac_check(required_role):
    """
    Enhanced RBAC decorator with common security checks, including MFA if enabled.
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        @_apply_base_security_checks # Apply the common security checks
        def decorated_function(*args, **kwargs):
            try:
                user_id = get_jwt_identity() # User ID and g.user is now guaranteed to be populated and active

                # The original rbac_check logic
                user_info = g.user # g.user is already populated by _common_auth_check
                if user_info['role'] != required_role:
                    security_logger.warning({
                        'message': 'RBAC Access Denied',
                        'userId': user_id,
                        'requiredRole': required_role,
                        'userRole': user_info['role'],
                        'endpoint': request.path,
                        'ip': request.remote_addr,
                        'request_id': getattr(g, 'request_id', 'unknown')
                    })
                    return jsonify({'error': 'Forbidden: Insufficient permissions.'}), 403

                security_logger.info(f"User {user_id} granted access with role {required_role} to {request.path}")
                return f(*args, **kwargs)
            except Exception as e:
                security_logger.error(f"Unhandled error in rbac_check for {request.path}: {e}", exc_info=True)
                return jsonify(status="error", message="An internal server error occurred during role check."), 500
        return decorated_function
    return decorator

class Permissions:
    """
    Defines constants for all permissions in the system to avoid magic strings.
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


# Configure basic logging (usually done in your main app.py or config)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Set security logger to capture WARN and above
logging.getLogger('security').setLevel(logging.WARNING)
# Set the current module's logger to DEBUG to see more internal RBAC logs
logging.getLogger(__name__).setLevel(logging.DEBUG)
