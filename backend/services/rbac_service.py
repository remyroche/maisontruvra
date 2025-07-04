import logging

from backend.database import db
from backend.models.user_models import User, UserRole
from backend.services.exceptions import (
    NotFoundException,
    ValidationException,
)

logger = logging.getLogger(__name__)
security_logger = logging.getLogger("security")


class RBACService:
    """
    Role-Based Access Control Service.
    Manages user roles and permissions in the system.
    """

    def __init__(self):
        # Maps role name to a set of permissions
        self._role_permissions = {
            "Admin": {
                "MANAGE_USERS",
                "VIEW_REPORTS",
                "DELETE_DATA",
                "MANAGE_PRODUCTS",
                "VIEW_INVENTORY",
                "FULL_ACCESS",
                "ADMIN_ACCESS",
                "VIEW_USERS",
                "VIEW_B2B_ACCOUNTS",
                "MANAGE_B2B_ACCOUNTS",
                "VIEW_PRODUCTS",
                "VIEW_ORDERS",
                "MANAGE_ORDERS",
                "MANAGE_BLOG",
                "MANAGE_SITE_SETTINGS",
                "MANAGE_LOYALTY",
                "MANAGE_INVOICES",
                "VIEW_AUDIT_LOGS",
            },
            "Staff": {
                "VIEW_REPORTS",
                "PROCESS_ORDERS",
                "VIEW_PRODUCTS",
                "VIEW_ORDERS",
                "MANAGE_ORDERS",
            },
            "Manager": {
                "MANAGE_PRODUCTS",
                "VIEW_INVENTORY",
                "GENERATE_REPORTS",
                "VIEW_PRODUCTS",
                "VIEW_ORDERS",
                "MANAGE_ORDERS",
                "VIEW_REPORTS",
            },
            "Editor": {"CREATE_CONTENT", "EDIT_CONTENT", "UPLOAD_MEDIA", "MANAGE_BLOG"},
            "Viewer": {"VIEW_CONTENT", "DOWNLOAD_REPORTS"},
            "B2B": {
                "VIEW_B2B_DASHBOARD",
                "ACCESS_B2B_DATA",
                "VIEW_PRODUCTS",
                "VIEW_ORDERS",
            },
            "Customer": {"VIEW_PRODUCTS", "PLACE_ORDERS", "VIEW_OWN_ORDERS"},
        }
        security_logger.info(
            "RBACService initialized with default roles and permissions."
        )

    def _get_user_roles_from_db(self, user_id):
        """
        Fetch user roles from the database.
        Returns a set of role names.
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return set()

            # Get roles from the user's role relationship
            if hasattr(user, "roles") and user.roles:
                return {role.name for role in user.roles}
            elif hasattr(user, "role") and user.role:
                # If user has a single role field
                return {
                    user.role.name if hasattr(user.role, "name") else str(user.role)
                }
            else:
                return set()

        except Exception as e:
            logger.error(f"Error fetching roles for user {user_id}: {str(e)}")
            return set()

    def _get_role_permissions_from_storage(self, role_name):
        """
        Get permissions for a specific role.
        Returns a set of permission strings.
        """
        return self._role_permissions.get(role_name, set())

    def add_user(self, user_id):
        """Adds a user to the RBAC system, initially with no roles."""
        try:
            user = User.query.get(user_id)
            if user:
                security_logger.info(f"User '{user_id}' exists in RBACService.")
            else:
                security_logger.warning(f"User '{user_id}' not found in database.")
        except Exception as e:
            logger.error(f"Error adding user {user_id} to RBAC: {str(e)}")

    def assign_role(self, user_id, role_name):
        """Assigns a role to a user."""
        try:
            user = User.query.get(user_id)
            if not user:
                security_logger.warning(
                    f"Cannot assign role '{role_name}' to non-existent user '{user_id}'."
                )
                return False

            if role_name not in self._role_permissions:
                security_logger.warning(
                    f"Attempted to assign undefined role '{role_name}' to user '{user_id}'."
                )
                return False

            # Create or get the role
            role = UserRole.query.filter_by(name=role_name).first()
            if not role:
                role = UserRole(name=role_name)
                db.session.add(role)

            # Assign role to user (this depends on your User-Role relationship)
            if hasattr(user, "roles"):
                if role not in user.roles:
                    user.roles.append(role)
                    db.session.commit()
                    security_logger.info(
                        f"Assigned role '{role_name}' to user '{user_id}'."
                    )
                    return True
            else:
                # If user has a single role field
                user.role = role
                db.session.commit()
                security_logger.info(
                    f"Assigned role '{role_name}' to user '{user_id}'."
                )
                return True

        except Exception as e:
            db.session.rollback()
            logger.error(
                f"Error assigning role '{role_name}' to user '{user_id}': {str(e)}"
            )
            return False

    def remove_role(self, user_id, role_name):
        """Removes a role from a user."""
        try:
            user = User.query.get(user_id)
            if not user:
                security_logger.warning(
                    f"Cannot remove role from non-existent user '{user_id}'."
                )
                return False

            role = UserRole.query.filter_by(name=role_name).first()
            if not role:
                security_logger.debug(f"Role '{role_name}' does not exist.")
                return False

            if hasattr(user, "roles") and role in user.roles:
                user.roles.remove(role)
                db.session.commit()
                security_logger.info(
                    f"Removed role '{role_name}' from user '{user_id}'."
                )
                return True
            else:
                security_logger.debug(
                    f"User '{user_id}' does not have role '{role_name}'."
                )
                return False

        except Exception as e:
            db.session.rollback()
            logger.error(
                f"Error removing role '{role_name}' from user '{user_id}': {str(e)}"
            )
            return False

    def get_user_roles(self, user_id):
        """Retrieves all roles assigned to a user."""
        return list(self._get_user_roles_from_db(user_id))

    def user_has_role(self, user_id, role_name):
        """Checks if a user has a specific role."""
        return role_name in self._get_user_roles_from_db(user_id)

    def user_has_permission(self, user_id, permission):
        """
        Checks if a user has a specific permission via any of their roles.
        This aggregates permissions from all roles the user has.
        """
        user_roles = self._get_user_roles_from_db(user_id)
        for role in user_roles:
            if permission in self._get_role_permissions_from_storage(role):
                return True
        return False

    def user_has_permissions(self, user_id, *required_permissions):
        """
        Checks if a user has ALL of the specified permissions.
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
        return self.user_has_role(user_id, "Staff")

    def user_is_admin(self, user_id):
        """
        Checks if a user is an admin.
        """
        return self.user_has_role(user_id, "Admin")

    def get_role_permissions(self, role_name):
        """Get all permissions for a specific role."""
        return list(self._get_role_permissions_from_storage(role_name))

    def get_all_roles(self):
        """Get all available roles."""
        return list(self._role_permissions.keys())

    def get_all_permissions(self):
        """Get all available permissions."""
        all_permissions = set()
        for permissions in self._role_permissions.values():
            all_permissions.update(permissions)
        return list(all_permissions)

    def create_role(self, role_name, permissions=None):
        """Create a new role with specified permissions."""
        if permissions is None:
            permissions = set()

        if role_name in self._role_permissions:
            raise ValidationException(f"Role '{role_name}' already exists")

        self._role_permissions[role_name] = set(permissions)
        security_logger.info(
            f"Created new role '{role_name}' with permissions: {permissions}"
        )
        return True

    def update_role_permissions(self, role_name, permissions):
        """Update permissions for an existing role."""
        if role_name not in self._role_permissions:
            raise NotFoundException(f"Role '{role_name}' not found")

        self._role_permissions[role_name] = set(permissions)
        security_logger.info(
            f"Updated permissions for role '{role_name}': {permissions}"
        )
        return True

    def delete_role(self, role_name):
        """Delete a role (be careful with this!)."""
        if role_name not in self._role_permissions:
            raise NotFoundException(f"Role '{role_name}' not found")

        # Don't allow deletion of critical roles
        if role_name in ["Admin", "Staff"]:
            raise ValidationException(f"Cannot delete critical role '{role_name}'")

        del self._role_permissions[role_name]
        security_logger.warning(f"Deleted role '{role_name}'")
        return True


# Create a singleton instance
rbac_service = RBACService()
