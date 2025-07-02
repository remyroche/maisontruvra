"""
This module defines the API endpoints for user management in the admin panel.
It leverages the @api_resource_handler to create clean, secure, and consistent CRUD endpoints,
and includes separate endpoints for specialized user actions.
"""
from flask import Blueprint, request, g, jsonify
from ..models import User
from ..schemas import AdminUserSchema, RoleSchema, TierAssignmentSchema, CustomDiscountSchema # Assuming these new schemas exist
from ..utils.decorators import api_resource_handler, roles_required
from ..services.user_service import UserService
from ..services.rbac_service import RBACService
from ..services.discount_service import DiscountService

from flask import Blueprint, request, g, jsonify
from flask_jwt_extended import jwt_required

from backend.models.user_models import User
from backend.schemas import UserSchema, UserUpdateSchema
from backend.services.user_service import UserService
from backend.services.exceptions import ServiceException
from backend.utils.decorators import api_resource_handler, roles_required

# --- Blueprint Setup ---
bp = Blueprint('user_management', __name__, url_prefix='/api/admin/users')

@bp.route('/', methods=['GET'])
@jwt_required()
@roles_required('Admin')
def get_all_users():
    """
    Retrieves a list of all users.
    This route is kept separate as it operates on a list, not a single resource.
    """
    try:
        # The service layer handles fetching all users, including soft-deleted ones if needed.
        # We can add a query param to include/exclude soft-deleted users.
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        users = UserService.get_all_users(include_deleted=include_deleted)
        return jsonify(UserSchema(many=True).dump(users)), 200
    except ServiceException as e:
        return jsonify(e.to_dict()), e.status_code

@bp.route('/', methods=['POST'])
@jwt_required()
@roles_required('Admin')
@api_resource_handler(model=User, request_schema=UserSchema, response_schema=UserSchema, log_action=True)
def create_user():
    """
    Creates a new user.
    The decorator handles validation, session management, and response serialization.
    """
    # The service call handles the business logic (e.g., password hashing).
    return UserService.create_user(g.validated_data)

@bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
@roles_required('Admin')
@api_resource_handler(model=User, response_schema=UserSchema, eager_loads=['roles'])
def get_user(user_id):
    """
    Retrieves a single user by their ID.
    The decorator handles fetching and serialization.
    """
    return g.target_object

@bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@roles_required('Admin')
@api_resource_handler(model=User, request_schema=UserSchema, response_schema=UserSchema, eager_loads=['roles'], log_action=True)
def update_user(user_id):
    """
    Updates an existing user's details.
    The decorator fetches the user, validates input, and handles the response.
    """
    # The service call handles the specific update logic.
    return UserService.update_user(g.target_object, g.validated_data)

@bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@roles_required('Admin')
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

@bp.route('/<int:user_id>/restore', methods=['POST'])
@jwt_required()
@roles_required('Admin')
@api_resource_handler(model=User, response_schema=UserSchema, log_action=True)
def restore_user(user_id):
    """
    Restores a soft-deleted user.
    The decorator handles all fetching and restoration logic automatically.
    """
    # The function body is intentionally empty as the decorator handles the full operation.
    return g.target_object


# --- Specialized User Actions ---

@bp.route('/<int:user_id>/roles', methods=['POST'])
@roles_required('Admin', 'Manager')
@api_resource_handler(model=User, request_schema=RoleSchema) # Use decorator to fetch user and validate role data
def assign_role_to_user(user_id):
    """Assigns a role to a user."""
    user = g.target_object
    role_name = g.validated_data['name']
    RBACService.assign_role_to_user(user, role_name)
    return jsonify({"message": f"Role '{role_name}' assigned to user {user.email}."})

@bp.route('/<int:user_id>/roles/<string:role_name>', methods=['DELETE'])
@roles_required('Admin', 'Manager')
@api_resource_handler(model=User) # Use decorator just to fetch the user
def remove_role_from_user(user_id, role_name):
    """Removes a role from a user."""
    user = g.target_object
    RBACService.remove_role_from_user(user, role_name)
    return jsonify({"message": f"Role '{role_name}' removed from user {user.email}."})

@bp.route('/<int:user_id>/assign-tier', methods=['POST'])
@roles_required('Admin', 'Manager')
@api_resource_handler(model=User, request_schema=TierAssignmentSchema)
def assign_tier_to_user(user_id):
    """Manually assigns a loyalty tier to a user."""
    user = g.target_object
    tier_id = g.validated_data['tier_id']
    DiscountService.assign_tier_to_user(user.id, tier_id)
    return jsonify({'message': f'Tier manually assigned to {user.email} successfully'})

@bp.route('/<int:user_id>/custom-discount', methods=['POST'])
@roles_required('Admin', 'Manager')
@api_resource_handler(model=User, request_schema=CustomDiscountSchema)
def set_custom_discount(user_id):
    """Sets a custom discount and spend limit for a user."""
    user = g.target_object
    data = g.validated_data
    DiscountService.set_custom_discount_for_user(
        user.id,
        data['discount_percentage'],
        data['monthly_spend_limit']
    )
    return jsonify({'message': 'Custom discount set successfully for user'})
