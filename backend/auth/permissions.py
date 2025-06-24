from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from backend.services.rbac_service import RBACService
_current_user_identity = None
_current_jwt_claims = {}

def verify_jwt_in_request():
    """Simulates JWT verification."""
    global _current_user_identity
    if _current_user_identity is None:
        raise Exception("No JWT in request (simulated). Call set_test_jwt_identity() first.")
    print(f"JWT verified for user: {_current_user_identity}")

def get_jwt_identity():
    """Simulates getting user identity from JWT."""
    return _current_user_identity

def get_jwt():
    """Simulates getting all claims from JWT."""
    return _current_jwt_claims

# Helper functions for testing/demonstration
def set_test_jwt_identity(user_id, claims=None):
    """Sets a simulated JWT identity for testing."""
    global _current_user_identity, _current_jwt_claims
    _current_user_identity = user_id
    _current_jwt_claims = claims if claims is not None else {}
    print(f"Test JWT identity set to: {user_id} with claims: {_current_jwt_claims}")

def clear_test_jwt_identity():
    """Clears the simulated JWT identity."""
    global _current_user_identity, _current_jwt_claims
    _current_user_identity = None
    _current_jwt_claims = {}
    print("Test JWT identity cleared.")


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
            # Add more roles and their permissions here
        }
        print("RBACService initialized with default roles and permissions.")
        print(f"Initial Role Permissions: {self._role_permissions}")

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
            print(f"User '{user_id}' added to RBACService.")
        else:
            print(f"User '{user_id}' already exists in RBACService.")

    def assign_role(self, user_id, role_name):
        """Assigns a role to a user."""
        if user_id not in self._user_roles:
            self.add_user(user_id) # Ensure user exists
        if role_name in self._role_permissions: # Check if role is defined
            self._user_roles[user_id].add(role_name)
            print(f"Assigned role '{role_name}' to user '{user_id}'. Current roles: {self._user_roles[user_id]}")
        else:
            print(f"Warning: Role '{role_name}' is not defined in RBACService._role_permissions.")

    def remove_role(self, user_id, role_name):
        """Removes a role from a user."""
        if user_id in self._user_roles and role_name in self._user_roles[user_id]:
            self._user_roles[user_id].remove(role_name)
            print(f"Removed role '{role_name}' from user '{user_id}'. Current roles: {self._user_roles[user_id]}")
        else:
            print(f"User '{user_id}' does not have role '{role_name}'.")

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


# Instantiate the RBACService (this would typically be a singleton or dependency injected)
RBACService = RBACService()


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
                    print(f"User {user_id} is Admin, granting access.")
                    return fn(*args, **kwargs)

                # 2. Permission check: If not an admin, check for all required permissions.
                if not RBACService.user_has_permissions(user_id, *required_permissions):
                    perms_str = ", ".join(required_permissions)
                    print(f"User {user_id} lacks required permissions or Admin role. Required: {perms_str}")
                    return jsonify(status="error", message=f"Insufficient permissions. Requires: {perms_str} or Admin role."), 403

                print(f"User {user_id} has all required permissions: {required_permissions}. Granting access.")
                return fn(*args, **kwargs)
            except Exception as e:
                print(f"Error during permissions_required check: {e}")
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
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()

            if not user_id:
                return jsonify(status="error", message="Authentication required."), 401
            if not RBACService.user_has_role(user_id, 'Admin'):
                print(f"User {user_id} is not Admin. Access denied.")
                return jsonify(status="error", message="Administrator access required."), 403
            print(f"User {user_id} is Admin. Granting access.")
            return fn(*args, **kwargs)
        except Exception as e:
            print(f"Error during admin_required check: {e}")
            # Log the exception e
            return jsonify(status="error", message="An error occurred during admin check."), 500
    return wrapper

def staff_required(fn):
    """
    A decorator to protect routes that require staff privileges.
    It checks for a staff role and, if MFA is enabled for that user,
    ensures the JWT indicates that MFA has been verified.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()

            if not user_id:
                return jsonify(status="error", message="Authentication required."), 401

            # Check if the user has a staff role via the RBAC service.
            if not RBACService.user_is_staff(user_id):
                print(f"User {user_id} is not staff. Access denied.")
                return jsonify(status="error", message="Staff account required."), 403

            # This assumes the login flow adds an 'mfa_verified' claim to the JWT
            # if the user has MFA enabled and has successfully passed the second factor.
            # A more robust implementation might re-verify with the database in some cases.
            claims = get_jwt()
            if claims.get("mfa_required") and not claims.get("mfa_verified"):
                print(f"User {user_id} requires MFA but it's not verified.")
                return jsonify(status="error", message="Multi-Factor Authentication is required for this action."), 403

            print(f"User {user_id} is staff and MFA status is okay. Granting access.")
            return fn(*args, **kwargs)
        except Exception as e:
            print(f"Error during staff_required check: {e}")
            # Log the exception e
            return jsonify(status="error", message="An error occurred during staff check."), 500
    return wrapper

def roles_required(*required_roles):
    """
    Decorator that checks if a user has at least ONE of the specified roles.
    This provides a flexible way to restrict access based on broader roles
    rather than granular permissions, or to allow multiple roles for a single endpoint.

    Usage:
    @roles_required('Manager', 'Editor') # User needs to be EITHER Manager OR Editor
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()

                if not user_id:
                    return jsonify(status="error", message="Authentication required."), 401

                user_roles = RBACService.get_user_roles(user_id)

                # Check if the user has any of the required roles
                has_required_role = any(role in user_roles for role in required_roles)

                if not has_required_role:
                    roles_str = ", ".join(required_roles)
                    print(f"User {user_id} does not have any of the required roles: {required_roles}. Access denied.")
                    return jsonify(status="error", message=f"Access denied. One of these roles is required: {roles_str}."), 403

                print(f"User {user_id} has one of the required roles: {required_roles}. Granting access.")
                return fn(*args, **kwargs)
            except Exception as e:
                print(f"Error during roles_required check: {e}")
                # Log the exception e
                return jsonify(status="error", message="An error occurred during role check."), 500
        return wrapper
    return decorator

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

