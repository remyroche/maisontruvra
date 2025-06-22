from flask import Blueprint, request, jsonify
from backend.services.user_service import UserService
from backend.services.rbac_service import RBACService
from backend.services.exceptions import NotFoundException, ServiceException
from backend.auth.permissions import admin_required

user_management_routes = Blueprint('user_management_routes', __name__)

@user_management_routes.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get a paginated list of all users."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    users_page = UserService.get_all_users(page, per_page)
    return jsonify({
        "users": [user.to_dict_admin() for user in users_page.items],
        "total": users_page.total,
        "pages": users_page.pages,
        "current_page": users_page.page
    }), 200

@user_management_routes.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get details for a specific user."""
    try:
        user = UserService.get_user_by_id(user_id)
        return jsonify(user.to_dict_admin()), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404

@user_management_routes.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update a user's details."""
    data = request.get_json()
    try:
        user = UserService.update_user(user_id, data)
        return jsonify(user.to_dict_admin()), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except ServiceException as e:
        return jsonify({"error": str(e)}), 400

@user_management_routes.route('/users/<int:user_id>/roles', methods=['POST'])
@admin_required
def assign_role_to_user(user_id):
    """Assign a role to a user."""
    data = request.get_json()
    role_name = data.get('role_name')
    if not role_name:
        return jsonify({"error": "Role name is required"}), 400
    try:
        RBACService.assign_role_to_user(user_id, role_name)
        return jsonify({"message": f"Role '{role_name}' assigned to user {user_id}"}), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404

@user_management_routes.route('/roles', methods=['GET'])
@admin_required
def get_roles():
    """Get all available roles."""
    roles = RBACService.get_all_roles()
    return jsonify([role.to_dict() for role in roles]), 200