"""
This module defines the API endpoints for user management in the admin panel.
It leverages the @api_resource_handler to create clean, secure, and consistent CRUD endpoints,
and includes separate endpoints for specialized user actions.
"""

from flask import Blueprint, g, jsonify, request
from flask_jwt_extended import jwt_required

from backend.models.user_models import User
from backend.schemas import UserSchema, UserUpdateSchema
from backend.services.user_service import UserService
from backend.utils.decorators import api_resource_handler, roles_required

from ..models import User
from ..schemas import (
    CustomDiscountSchema,
    RoleSchema,
    TierAssignmentSchema,
)  # Assuming these new schemas exist
from ..services.discount_service import DiscountService
from ..services.rbac_service import RBACService
from ..services.user_service import UserService
from ..utils.decorators import api_resource_handler, roles_required

# --- Blueprint Setup ---
bp = Blueprint("user_management", __name__, url_prefix="/api/admin/users")

from flask import Blueprint
from pydantic import ValidationError

from backend.services.auth_service import AuthService
from backend.services.exceptions import UpdateException, UserNotFoundException

user_management_bp = Blueprint(
    "user_management_bp", __name__, url_prefix="/api/admin/users"
)

user_service = UserService()
auth_service = AuthService()


@user_management_bp.route("/", methods=["GET"])
@roles_required("Admin", "Manager", "Staff")
def get_all_users():
    """
    Retrieves all users.
    Accessible only by admins.
    """
    users = user_service.get_all_users_with_details()
    return jsonify([user.to_dict() for user in users]), 200


@user_management_bp.route("/<user_id>", methods=["GET"])
@roles_required("Admin", "Manager", "Staff")
def get_user(user_id):
    """
    Retrieves a single user by their ID.
    Accessible only by admins.
    """
    try:
        user = user_service.get_user_by_id(user_id)
        return jsonify(user.to_dict()), 200
    except UserNotFoundException as e:
        return jsonify({"error": str(e)}), 404


@user_management_bp.route("/<user_id>", methods=["PUT"])
@roles_required("Admin", "Manager")
def update_user(user_id):
    """
    Updates a user's details.
    Accessible only by admins.
    """
    data = request.get_json()
    try:
        UserUpdateSchema.model_validate(data)
        user = user_service.update_user(user_id, data)
        return jsonify(user.to_dict()), 200
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except (UserNotFoundException, UpdateException) as e:
        return jsonify({"error": str(e)}), 404


@user_management_bp.route("/<user_id>/deactivate", methods=["POST"])
@roles_required("Admin", "Manager")
def deactivate_user_account(user_id):
    """
    Deactivates a user's account.
    Accessible only by admins.
    """
    try:
        user_service.deactivate_user(user_id)
        return jsonify({"message": "User deactivated successfully"}), 200
    except UserNotFoundException as e:
        return jsonify({"error": str(e)}), 404


@user_management_bp.route("/<user_id>/activity", methods=["GET"])
@roles_required("Admin", "Manager", "Dev")
def get_user_activity_log(user_id):
    """
    Retrieves the activity log for a specific user.
    Accessible only by admins.
    """
    try:
        activity = user_service.get_user_activity(user_id)
        return jsonify(activity), 200
    except UserNotFoundException as e:
        return jsonify({"error": str(e)}), 404


@user_management_bp.route("/roles", methods=["GET"])
@roles_required("Admin", "Manager", "Staff")
def get_roles():
    """
    Retrieves all available roles.
    Accessible only by admins.
    """
    roles = auth_service.get_all_roles()
    return jsonify([role.to_dict() for role in roles]), 200


@bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
@roles_required("Admin")
@api_resource_handler(model=User, allow_hard_delete=True, log_action=True)
def delete_user(user_id):
    """
    Deletes a user.
    - Soft-delete by default.
    - Use ?hard=true for a permanent, irreversible delete.
    The decorator handles all fetching and deletion logic automatically.
    """
    # The function body is intentionally empty as the decorator handles the full operation.
    return None


@bp.route("/<int:user_id>/restore", methods=["POST"])
@jwt_required()
@roles_required("Admin")
@api_resource_handler(model=User, response_schema=UserSchema, log_action=True)
def restore_user(user_id):
    """
    Restores a soft-deleted user.
    The decorator handles all fetching and restoration logic automatically.
    """
    # The function body is intentionally empty as the decorator handles the full operation.
    return g.target_object


# --- Specialized User Actions ---


@bp.route("/<int:user_id>/roles", methods=["POST"])
@roles_required("Admin", "Manager")
@api_resource_handler(
    model=User, request_schema=RoleSchema
)  # Use decorator to fetch user and validate role data
def assign_role_to_user(user_id):
    """Assigns a role to a user."""
    user = g.target_object
    role_name = g.validated_data["name"]
    RBACService.assign_role_to_user(user, role_name)
    return jsonify({"message": f"Role '{role_name}' assigned to user {user.email}."})


@bp.route("/<int:user_id>/roles/<string:role_name>", methods=["DELETE"])
@roles_required("Admin", "Manager")
@api_resource_handler(model=User)  # Use decorator just to fetch the user
def remove_role_from_user(user_id, role_name):
    """Removes a role from a user."""
    user = g.target_object
    RBACService.remove_role_from_user(user, role_name)
    return jsonify({"message": f"Role '{role_name}' removed from user {user.email}."})


@bp.route("/<int:user_id>/assign-tier", methods=["POST"])
@roles_required("Admin", "Manager")
@api_resource_handler(model=User, request_schema=TierAssignmentSchema)
def assign_tier_to_user(user_id):
    """Manually assigns a loyalty tier to a user."""
    user = g.target_object
    tier_id = g.validated_data["tier_id"]
    DiscountService.assign_tier_to_user(user.id, tier_id)
    return jsonify({"message": f"Tier manually assigned to {user.email} successfully"})


@bp.route("/<int:user_id>/custom-discount", methods=["POST"])
@roles_required("Admin", "Manager")
@api_resource_handler(model=User, request_schema=CustomDiscountSchema)
def set_custom_discount(user_id):
    """Sets a custom discount and spend limit for a user."""
    user = g.target_object
    data = g.validated_data
    DiscountService.set_custom_discount_for_user(
        user.id, data["discount_percentage"], data["monthly_spend_limit"]
    )
    return jsonify({"message": "Custom discount set successfully for user"})
