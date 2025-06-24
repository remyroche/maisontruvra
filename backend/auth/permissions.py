from functools import wraps
from flask import jsonify, request, g # Import request and g for access within decorators
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt, jwt_required # Ensure jwt_required is imported
import logging

# Assuming these utilities exist from previous implementations
from backend.services.rbac_service import RBACService
from backend.utils.csrf_protection import CSRFProtection # Assuming this is available
from backend.models.user_models import User # Assuming your User model is here

# It's good practice to get loggers this way.
logger = logging.getLogger(__name__)
security_logger = logging.getLogger('security') # Use the dedicated security logger


# Instantiate the RBACService (this would typically be a singleton or dependency injected)
# Ensure RBACService is defined before being instantiated here.
# For demonstration purposes, I'll keep the RBACService class here,
# but in a real app, it would be imported from backend.services.rbac_service
# as per your import statement.

# --- Start of RBACService for self-contained demonstration ---
# This part is included for the immersive to be runnable on its own.
# In your actual project, RBACService would be imported from backend.services.rbac_service
class RBACService:
    """
    A conceptual Role-Based Access Control Service.
    In a real application, this would interact with a database
    (e.g., SQL, NoSQL) to store and retrieve user roles and
    role-permission mappings.

    For demonstration, we use in-memory dictionaries.
    """
    def __init__(self):
        # Maps user_id to a set of role names
        self._user_roles = {} # Example: {"user123": {"Admin", "Editor"}}

        # Maps role name to a set of permissions
        self._role_permissions = {
            "Admin": {"MANAGE_USERS", "VIEW_REPORTS", "DELETE_DATA", "MANAGE_PRODUCTS", "VIEW_INVENTORY", "FULL_ACCESS"},
            "Staff": {"VIEW_REPORTS", "PROCESS_ORDERS"}, # Staff might have specific permissions
            "Manager": {"MANAGE_PRODUCTS", "VIEW_INVENTORY", "GENERATE_REPORTS"},
            "Editor": {"CREATE_CONTENT", "EDIT_CONTENT", "UPLOAD_MEDIA"},
            "Viewer": {"VIEW_CONTENT", "DOWNLOAD_REPORTS"},
            "B2B": {"VIEW_B2B_DASHBOARD", "ACCESS_B2B_DATA"}, # New B2B permissions
            # Add more roles and their permissions here
        }
        security_logger.info("RBACService initialized with default roles and permissions.")
        # print(f"Initial Role Permissions: {self._role_permissions}") # Avoid printing sensitive structure directly

    def _get_user_roles_from_storage(self, user_id):
        """
        Simulates fetching user roles from a database.
        Returns a set of role names.
        """
        return self._user_roles.get(user_id, set())

    def _get_role_permissions_from_storage(self, role_name):
        """
        Simulates fetching permissions for a specific role from a database.
        Returns a set of permission strings.
        """
        return self._role_permissions.get(role_name, set())

    def add_user(self, user_id):
        """Adds a user to the RBAC system, initially with no roles."""
        if user_id not in self._user_roles:
            self._user_roles[user_id] = set()
            security_logger.info(f"User '{user_id}' added to RBACService.")
        else:
            security_logger.debug(f"User '{user_id}' already exists in RBACService.")

    def assign_role(self, user_id, role_name):
        """Assigns a role to a user."""
        if user_id not in self._user_roles:
            self.add_user(user_id) # Ensure user exists
        if role_name in self._role_permissions: # Check if role is defined
            self._user_roles[user_id].add(role_name)
            security_logger.info(f"Assigned role '{role_name}' to user '{user_id}'.")
        else:
            security_logger.warning(f"Attempted to assign undefined role '{role_name}' to user '{user_id}'.")

    def remove_role(self, user_id, role_name):
        """Removes a role from a user."""
        if user_id in self._user_roles and role_name in self._user_roles[user_id]:
            self._user_roles[user_id].remove(role_name)
            security_logger.info(f"Removed role '{role_name}' from user '{user_id}'.")
        else:
            security_logger.debug(f"User '{user_id}' does not have role '{role_name}' or user not found.")

    def get_user_roles(self, user_id):
        """Retrieves all roles assigned to a user."""
        return list(self._get_user_roles_from_storage(user_id)) # Return as list for convenience

    def user_has_role(self, user_id, role_name):
        """Checks if a user has a specific role."""
        return role_name in self._get_user_roles_from_storage(user_id)

    def user_has_permission(self, user_id, permission):
        """
        Checks if a user has a specific permission via any of their roles.
        This aggregates permissions from all roles the user has.
        """
        user_roles = self._get_user_roles_from_storage(user_id)
        for role in user_roles:
            if permission in self._get_role_permissions_from_storage(role):
                return True
        return False

    def user_has_permissions(self, user_id, *required_permissions):
        """
        Checks if a user has ALL of the specified permissions.
        Iterates through required permissions and uses user_has_permission.
        """
        for perm in required_permissions:
            if not self.user_has_permission(user_id, perm):
                return False
        return True

    def user_is_staff(self, user_id):
        """
        Checks if a user is considered 'staff'.
        This can be defined by having a specific 'Staff' role or other criteria.
        """
        return self.user_has_role(user_id, 'Staff')
# --- End of RBACService for self-contained demonstration ---

# Instantiate RBACService
RBACService = RBACService()

# --- Placeholder for CSRFProtection and User Model for self-contained demonstration ---
# In your actual project, these would be imported from their respective paths.
class CSRFProtection:
    @staticmethod
    def validate_csrf_token():
        # In a real app, this would check headers/cookies for a valid token
        # For demonstration, we'll simulate a failure for testing
        if request.headers.get('X-CSRF-TOKEN') != 'valid-csrf-token':
            raise Exception("Invalid CSRF token")
        security_logger.info("CSRF token validated successfully.")

class User:
    # A simplified User model for demonstration
    _users_db = {} # user_id -> User object
    class Role:
        def __init__(self, value):
            self.value = value
    def __init__(self, id, email, role, is_active=True):
        self.id = id
        self.email = email
        self.role = self.Role(role)
        self.is_active = is_active
        User._users_db[id] = self

    @staticmethod
    def query_get(user_id): # Simulates ORM query.get
        return User._users_db.get(user_id)


def _common_auth_check(fn, user_id):
    """
    Helper function to perform common authentication and user status checks.
    """
    if not user_id:
        security_logger.warning({
            'message': 'Unauthenticated access attempt',
            'endpoint': request.path,
            'ip': request.remote_addr,
            'request_id': getattr(g, 'request_id', 'unknown')
        })
        return jsonify(status="error", message="Authentication required."), 401

    user = User.query_get(user_id) # Use the simplified static method for demonstration
    if not user:
        security_logger.warning({
            'message': 'User ID from JWT not found in DB',
            'userId': user_id,
            'endpoint': request.path,
            'ip': request.remote_addr,
            'request_id': getattr(g, 'request_id', 'unknown')
        })
        return jsonify(status="error", message="User not found."), 401

    if not user.is_active:
        security_logger.warning({
            'message': 'Inactive user access attempt',
            'userId': user_id,
            'endpoint': request.path,
            'ip': request.remote_addr,
            'request_id': getattr(g, 'request_id', 'unknown')
        })
        return jsonify(status="error", message="Account inactive."), 401

    # Store user info in g for use in the route
    g.user = {
        'id': user.id,
        'email': user.email,
        'role': user.role.value
    }
    security_logger.debug(f"User {user_id} authenticated and active. Role: {user.role.value}")
    return None # Indicates success, no error response


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
    return None # Indicates success, no error response

def _apply_base_security_checks(fn):
    """
    A helper decorator that performs common authentication, CSRF,
    and mandatory MFA checks (if MFA is enabled for the user).
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

        # Enforce MFA if enabled for the user
        mfa_error_response = _check_mfa_status()
        if mfa_error_response:
            return mfa_error_response

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
    Strengthened with logging, user status checks, and CSRF protection.
    """
    @wraps(fn)
    @jwt_required() # Ensure JWT is present and valid
    def wrapper(*args, **kwargs):
        try:
            user_id = get_jwt_identity()

            # Common authentication and user status check
            error_response = _common_auth_check(fn, user_id)
            if error_response:
                return error_response

            # CSRF protection for state-changing methods
            error_response = _csrf_and_state_change_check(fn)
            if error_response:
                return error_response

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
    Enhanced RBAC decorator with proper logging and CSRF protection.
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()

            # Common authentication and user status check
            error_response = _common_auth_check(f, user_id) # Note: Pass 'f' here not 'fn'
            if error_response:
                return error_response

            # CSRF protection for state-changing methods
            error_response = _csrf_and_state_change_check(f) # Note: Pass 'f' here not 'fn'
            if error_response:
                return error_response

            # The original rbac_check logic
            user = User.query_get(user_id) # g.user is already populated by _common_auth_check
            if user.role.value != required_role:
                security_logger.warning({
                    'message': 'RBAC Access Denied',
                    'userId': user_id,
                    'requiredRole': required_role,
                    'userRole': user.role.value,
                    'endpoint': request.path,
                    'ip': request.remote_addr,
                    'request_id': getattr(g, 'request_id', 'unknown')
                })
                return jsonify({'error': 'Forbidden: Insufficient permissions.'}), 403

            security_logger.info(f"User {user_id} granted access with role {required_role} to {request.path}")
            return f(*args, **kwargs) # Ensure 'f' is called here
        return decorated_function
    return decorator


# Configure basic logging (usually done in your main app.py or config)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Set security logger to capture WARN and above
logging.getLogger('security').setLevel(logging.WARNING)
# Set the current module's logger to DEBUG to see more internal RBAC logs
logging.getLogger(__name__).setLevel(logging.DEBUG)
