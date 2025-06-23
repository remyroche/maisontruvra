from flask import Blueprint, request, jsonify
from backend.services.user_service import UserService
from backend.models.user_models import User
from backend.utils.sanitization import sanitize_input
from backend.auth.permissions import permissions_required

user_management_bp = Blueprint('user_management_bp', __name__, url_prefix='/admin/users')

# READ all users (with pagination)
@user_management_bp.route('/', methods=['GET'])
@permissions_required('MANAGE_USERS')
@admin_required
def get_users():
    """
    Get a paginated list of all users.
    Query Params:
    - page: integer, the page number to retrieve.
    - per_page: integer, the number of users per page.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        # Assuming the service method is updated to handle pagination
        users_pagination = UserService.get_all_users_paginated(page=page, per_page=per_page)
        return jsonify({
            "status": "success",
            "data": [user.to_dict() for user in users_pagination.items],
            "total": users_pagination.total,
            "pages": users_pagination.pages,
            "current_page": users_pagination.page
        }), 200
    except Exception as e:
        # In a real app, log the error e
        return jsonify(status="error", message="An internal error occurred while fetching users."), 500

# READ a single user by ID
@user_management_bp.route('/<int:user_id>', methods=['GET'])
@permissions_required('MANAGE_USERS')
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
@permissions_required('MANAGE_USERS')
@admin_required
def create_user():
    """
    Create a new user. Expects a JSON body with user details.
    """
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Invalid or missing JSON body"), 400

    sanitized_data = sanitize_input(data)

    required_fields = ['email', 'password', 'first_name', 'last_name', 'role']
    if not all(field in sanitized_data for field in required_fields):
        missing_fields = [field for field in required_fields if field not in sanitized_data]
        return jsonify(status="error", message=f"Missing required fields: {', '.join(missing_fields)}"), 400

    if User.query.filter_by(email=sanitized_data['email']).first():
        return jsonify(status="error", message="User with this email already exists"), 409

    try:
        # Assuming the service handles hashing the password
        new_user = UserService.create_user(sanitized_data)
        return jsonify(status="success", data=new_user.to_dict()), 201
    except ValueError as e: # Catch specific validation errors from the service
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # In a real app, log the error e
        return jsonify(status="error", message="An internal error occurred while creating the user."), 500

# UPDATE an existing user
@user_management_bp.route('/<int:user_id>', methods=['PUT'])
@permissions_required('MANAGE_USERS')
@admin_required
def update_user(user_id):
    """
    Update an existing user's information.
    """
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Invalid or missing JSON body"), 400
    
    if not UserService.get_user_by_id(user_id):
        return jsonify(status="error", message="User not found"), 404

    sanitized_data = sanitize_input(data)
    # Prevent password from being updated through this endpoint for security.
    sanitized_data.pop('password', None)
    
    try:
        updated_user = UserService.update_user(user_id, sanitized_data)
        return jsonify(status="success", data=updated_user.to_dict()), 200
    except ValueError as e: # Catch specific validation errors from the service
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # In a real app, log the error e
        return jsonify(status="error", message="An internal error occurred while updating the user."), 500

# DELETE a user
@user_management_bp.route('/<int:user_id>', methods=['DELETE'])
@permissions_required('MANAGE_USERS')
@admin_required
def delete_user(user_id):
    """
    Delete a user.
    """
    if not UserService.get_user_by_id(user_id):
        return jsonify(status="error", message="User not found"), 404

    try:
        UserService.delete_user(user_id)
        return jsonify(status="success", message="User deleted successfully"), 200
    except Exception as e:
        # In a real app, log the error e
        return jsonify(status="error", message="An internal error occurred while deleting the user."), 500


