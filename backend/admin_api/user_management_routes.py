"""
This module defines the API endpoints for user management in the admin panel.
It leverages the @api_resource_handler to create clean, secure, and consistent CRUD endpoints,
and includes separate endpoints for specialized user actions.
"""

import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from backend.models.user_models import User
from backend.schemas import (
    CustomDiscountSchema,
    RoleSchema,
    TierAssignmentSchema,
    UserSchema,
)
from backend.services.auth_service import AuthService
from backend.services.discount_service import DiscountService
from backend.services.exceptions import UpdateException, UserNotFoundException
from backend.services.rbac_service import rbac_service
from backend.services.user_service import UserService
from backend.utils.decorators import api_resource_handler, roles_required

# --- Blueprint Setup ---
bp = Blueprint("user_management", __name__, url_prefix="/api/admin/users")

# --- Service Initialization ---
logger = logging.getLogger(__name__)
user_service = UserService(logger)
auth_service = AuthService(logger)
discount_service = DiscountService(logger)
# rbac_service is a singleton instance, so no need to instantiate


# --- CRUD Endpoints ---
@bp.route("/", methods=["GET"])
@roles_required("Admin", "Manager", "Staff")
def get_all_users():
    """
    Retrieves all users with their details.
    """
    users = user_service.get_all_users_with_details()
    return jsonify(UserSchema(many=True).dump(users)), 200


@bp.route("/<int:user_id>", methods=["GET"])
@roles_required("Admin", "Manager", "Staff")
def get_user(user_id):
    """
    Retrieves a single user by their ID.
    """
    try:
        user = user_service.get_user_by_id(user_id)
        return jsonify(UserSchema().dump(user)), 200
    except UserNotFoundException as e:
        return jsonify({"error": str(e)}), 404


@bp.route("/<int:user_id>", methods=["PUT"])
@roles_required("Admin", "Manager")
def update_user(user_id):
    """
    Updates a user's details.
    """
    data = request.get_json()
    try:
        # Pydantic validation can be used if you adopt it project-wide
        # For now, we'll pass the dict directly to the service
        user = user_service.update_user(user_id, data)
        return jsonify(UserSchema().dump(user)), 200
    except (UserNotFoundException, UpdateException) as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred"}), 500


@bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
@roles_required("Admin")
@api_resource_handler(model=User, allow_hard_delete=True, log_action=True)
def delete_user(instance):
    """
    Deletes a user.
    The decorator handles all fetching and deletion logic automatically.
    """
    return {"message": f"User {instance.email} deleted successfully."}


@bp.route("/<int:user_id>/restore", methods=["POST"])
@jwt_required()
@roles_required("Admin")
@api_resource_handler(model=User, response_schema=UserSchema, log_action=True)
def restore_user(instance):
    """
    Restores a soft-deleted user.
    """
    instance.deleted_at = None
    return instance


# --- Specialized User Actions ---


@bp.route("/<int:user_id>/roles", methods=["POST"])
@roles_required("Admin", "Manager")
@api_resource_handler(model=User, request_schema=RoleSchema)
def assign_role_to_user(instance, validated_data):
    """Assigns a role to a user."""
    user = instance
    role_name = validated_data["name"]
    rbac_service.assign_role(user.id, role_name)
    return jsonify({"message": f"Role '{role_name}' assigned to user {user.email}."})


@bp.route("/<int:user_id>/roles/<string:role_name>", methods=["DELETE"])
@roles_required("Admin", "Manager")
@api_resource_handler(model=User)
def remove_role_from_user(instance, role_name):
    """Removes a role from a user."""
    user = instance
    rbac_service.remove_role(user.id, role_name)
    return jsonify({"message": f"Role '{role_name}' removed from user {user.email}."})


@bp.route("/<int:user_id>/assign-tier", methods=["POST"])
@roles_required("Admin", "Manager")
@api_resource_handler(model=User, request_schema=TierAssignmentSchema)
def assign_tier_to_user_route(instance, validated_data):
    """Manually assigns a loyalty tier to a user."""
    user = instance
    tier_id = validated_data["tier_id"]
    discount_service.assign_tier_to_user(user.id, tier_id)
    return jsonify({"message": f"Tier manually assigned to {user.email} successfully"})


@bp.route("/<int:user_id>/custom-discount", methods=["POST"])
@roles_required("Admin", "Manager")
@api_resource_handler(model=User, request_schema=CustomDiscountSchema)
def set_custom_discount(instance, validated_data):
    """Sets a custom discount and spend limit for a user."""
    user = instance
    data = validated_data
    discount_service.set_custom_discount_for_user(
        user.id, data["discount_percentage"], data["monthly_spend_limit"]
    )
    return jsonify({"message": "Custom discount set successfully for user"})


@bp.route("/<int:user_id>/deactivate", methods=["POST"])
@roles_required("Admin", "Manager")
def deactivate_user_account(user_id):
    """
    Deactivates a user's account (soft delete).
    """
    try:
        user_service.deactivate_user(user_id)
        return jsonify({"message": "User deactivated successfully"}), 200
    except UserNotFoundException as e:
        return jsonify({"error": str(e)}), 404


@bp.route("/<int:user_id>/activity", methods=["GET"])
@roles_required("Admin", "Manager")
def get_user_activity_log(user_id):
    """
    Retrieves the activity log for a specific user.
    """
    try:
        activity = user_service.get_user_activity(user_id)
        return jsonify(activity), 200
    except UserNotFoundException as e:
        return jsonify({"error": str(e)}), 404


@bp.route("/roles", methods=["GET"])
@roles_required("Admin", "Manager", "Staff")
def get_roles():
    """
    Retrieves all available roles.
    """
    roles = rbac_service.get_all_roles()
    return jsonify(roles), 200
