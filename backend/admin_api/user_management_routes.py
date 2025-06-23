# backend/admin_api/user_management_routes.py

from flask import Blueprint, request, jsonify
from backend.services.user_service import UserService
from backend.models.user_models import User
from backend.utils.sanitization import sanitize_input
from backend.auth.permissions import permission_required
from backend.services.rbac_service import RBACService

user_management_bp = Blueprint('user_management_bp', __name__, url_prefix='/admin/users')

# READ all users (with pagination)
@user_management_bp.route('/', methods=['GET'])
@permission_required('MANAGE_USERS')
@admin_required
def get_users():
    """
    Get a paginated list of all users.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        users_pagination = UserService.get_all_users(page=page, per_page=per_page)
        return jsonify({
            "status": "success",
            "data": [user.to_dict() for user in users_pagination.items],
            "total": users_pagination.total,
            "pages": users_pagination.pages,
            "current_page": users_pagination.page
        }), 200
    except Exception as e:
        # Proper logging should be implemented here
        return jsonify(status="error", message=str(e)), 500


# READ a single user by ID
@user_management_bp.route('/<int:user_id>', methods=['GET'])
@permission_required('MANAGE_USERS')
@admin_required
def get_user(user_id):
    """
    Get a single user by their ID.
    """
    user = UserService.get_user_by_id(user_id)
    if user:
        return jsonify(status="success", data=user.to_dict()), 200
    return jsonify(status="error", message="User not found"), 404


# CREATE a new user
@user_management_bp.route('/', methods=['POST'])
@permission_required('MANAGE_USERS')
@admin_required
def create_user():
    """
    Create a new user.
    """
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Invalid JSON"), 400

    sanitized_data = sanitize_input(data)

    # Basic validation
    required_fields = ['email', 'password', 'first_name', 'last_name']
    if not all(field in sanitized_data for field in required_fields):
        return jsonify(status="error", message="Missing required fields"), 400

    # Check if user already exists
    if User.query.filter_by(email=sanitized_data['email']).first():
        return jsonify(status="error", message="User with this email already exists"), 409

    try:
        new_user = UserService.create_user(sanitized_data)
        return jsonify(status="success", data=new_user.to_dict()), 201
    except Exception as e:
        # Proper logging should be implemented here
        return jsonify(status="error", message=f"Could not create user: {e}"), 500


# UPDATE an existing user
@user_management_bp.route('/<int:user_id>', methods=['PUT'])
@permission_required('MANAGE_USERS')
@admin_required
def update_user(user_id):
    """
    Update an existing user's information.
    """
    user = UserService.get_user_by_id(user_id)
    if not user:
        return jsonify(status="error", message="User not found"), 404

    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Invalid JSON"), 400

    sanitized_data = sanitize_input(data)

    try:
        updated_user = UserService.update_user(user_id, sanitized_data)
        return jsonify(status="success", data=updated_user.to_dict()), 200
    except Exception as e:
        # Proper logging should be implemented here
        return jsonify(status="error", message=f"Could not update user: {e}"), 500


# DELETE a user
@user_management_bp.route('/<int:user_id>', methods=['DELETE'])
@permission_required('MANAGE_USERS')
@admin_required
def delete_user(user_id):
    """
    Delete a user.
    """
    user = UserService.get_user_by_id(user_id)
    if not user:
        return jsonify(status="error", message="User not found"), 404

    try:
        UserService.delete_user(user_id)
        return jsonify(status="success", message="User deleted successfully"), 200
    except Exception as e:
        # Proper logging should be implemented here
        return jsonify(status="error", message=f"Could not delete user: {e}"), 500
