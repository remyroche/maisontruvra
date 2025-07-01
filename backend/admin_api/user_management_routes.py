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

# --- Blueprint Setup ---
bp = Blueprint('user_management', __name__, url_prefix='/api/admin/users')

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@roles_required('Admin') # IMPORTANT: Only Admins can manage users.
@api_resource_handler(
    model=User,
    request_schema=AdminUserSchema,
    response_schema=AdminUserSchema,
    eager_loads=['roles'], # Eager load roles for performance
    log_action=True,
    allow_hard_delete=False # Default to soft delete for safety
)
def handle_users(user_id=None, is_hard_delete=False):
    """Handles all CRUD operations for Users from an admin perspective."""
    
    if request.method == 'GET' and user_id is None:
        all_users = UserService.get_all_users()
        return jsonify(AdminUserSchema(many=True).dump(all_users))

    if request.method == 'GET':
        return g.target_object

    elif request.method == 'POST':
        return UserService.create_user(g.validated_data)

    elif request.method == 'PUT':
        return UserService.update_user(g.target_object, g.validated_data)

    elif request.method == 'DELETE':
        if is_hard_delete:
            UserService.hard_delete_user(user_id)
        else:
            UserService.soft_delete_user(user_id)
        return None

# --- Specialized User Actions ---

@bp.route('/<int:user_id>/restore', methods=['PUT'])
@roles_required('Admin', 'Manager')
@api_resource_handler(model=User) # Use decorator just to fetch the user securely
def restore_user(user_id):
    """Restores a soft-deleted user."""
    UserService.restore_user(g.target_object)
    return jsonify({"message": "User restored successfully"})

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
