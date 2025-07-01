from flask import Blueprint, request, jsonify, g, current_user  
from backend.services.user_service import UserService
from backend.services.exceptions import NotFoundException, ValidationException, UnauthorizedException
from backend.middleware import sanitize_request_data
from backend.utils.input_sanitizer import InputSanitizer
from backend.services.audit_log_service import AuditLogService
from backend.utils.csrf_protection import CSRFProtection
import logging
from backend.utils.decorators import staff_required, roles_required, permissions_required, api_resource_handler
from backend.services.discount_service import DiscountService
from backend.models.user_models import User
from backend.schemas import UserSchema, UpdateUserSchema
from backend.utils.input_sanitizer import InputSanitizer
from decimal import Decimal
from flask_limiter import Limiter
from backend.middleware import RBACService
from backend.utils.decorators import admin_required, roles_required
from backend.services.exceptions import UserAlreadyExistsError
from marshmallow import ValidationError
from backend.schemas import AdminUserUpdateSchema, UserRegistrationSchema


logger = logging.getLogger(__name__)
security_logger = logging.getLogger('security')

user_management_bp = Blueprint('user_management', __name__)





@user_management_bp.route('/<int:user_id>', methods=['GET'])
@roles_required ('Admin', 'Manager')
def get_user(user_id):
    user_service = UserService()
    user = user_service.get_user_profile(user_id)
    return jsonify(user)


@user_management_bp.route('/<int:user_id>', methods=['PUT'])
@roles_required ('Admin', 'Manager')
def update_user(user_id):
    """ Admin endpoint to update a user. """
    schema = AdminUserUpdateSchema()
    try:
        data = schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user_service = UserService()
    try:
        updated_user = user_service.admin_update_user(user_id, data)
        if not updated_user:
            return jsonify({"error": "User not found."}), 404
        return jsonify({"message": "User updated successfully.", "user": updated_user.to_dict()})
    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        return jsonify({"error": "Failed to update user."}), 500

@user_management_bp.route('/', methods=['POST'])
@roles_required ('Admin', 'Manager')
def create_user():
    """ Admin endpoint to create a new user. """
    schema = UserRegistrationSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    user_service = UserService()
    try:
        user = user_service.admin_create_user(data)
        return jsonify({"message": "User created successfully", "user": user.to_dict()}), 201
    except UserAlreadyExistsError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 400


    @staticmethod
    def get_all_users_paginated(page, per_page, filters=None):
        """
        Retrieves a paginated list of users with filtering and sorting.
        Optimized to prevent N+1 queries for roles.
        """
        query = User.query.options(joinedload(User.roles))

        if filters:
            if filters.get('role'):
                query = query.join(User.roles).filter(Role.name == filters['role'])
            if filters.get('is_active') is not None:
                query = query.filter(User.is_active == filters['is_active'])
            if filters.get('email'):
                query = query.filter(User.email.ilike(f"%{filters['email']}%"))

        # Order by ID for consistent pagination results
        query = query.order_by(User.id.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination

@user_management_bp.route('/users/<int:user_id>', methods=['GET'])
@api_resource_handler(User, check_ownership=False)
@roles_required ('Admin', 'Manager')
def get_user_details(user_id):
    """
    Retrieves detailed information for a single user.
    C[R]UD - Read
    """
    # User is already validated and available as g.user
    return jsonify(g.user.to_admin_dict()) # Use a detailed serializer for admin views


@user_management_bp.route('/<int:user_id>/assign-tier', methods=['POST'])
@roles_required ('Admin', 'Manager')
@sanitize_request_data
def assign_tier_to_user(user_id):
    """
    Manually assigns a tier to any user. This action overrides automated tier assignments.
    """
    data = request.get_json()
    if not data or 'tier_id' not in data:
        return jsonify({'message': 'tier_id is required'}), 400
    
    try:
        user = DiscountService.assign_tier_to_user(user_id, data['tier_id'])
        return jsonify({'message': f'Tier manually assigned to {user.email} successfully'}), 200
    except NotFoundException as e:
        return jsonify({'message': str(e)}), 404
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

@user_management_bp.route('/<int:user_id>/custom-discount', methods=['POST'])
@roles_required ('Admin', 'Manager')
@sanitize_request_data
@limiter.limit("10 per minute")
def set_custom_discount(user_id):
    """
    Sets a custom discount percentage and monthly spend limit for any user.
    This overrides any tier-based discounts.
    """
    data = request.get_json()
    discount = data.get('discount_percentage')
    limit = data.get('monthly_spend_limit')

    if discount is None or limit is None:
        return jsonify({'message': 'discount_percentage and monthly_spend_limit are required'}), 400

    try:
        DiscountService.set_custom_discount_for_user(
            user_id,
            Decimal(discount),
            Decimal(limit)
        )
        return jsonify({'message': 'Custom discount set successfully for user'}), 200
    except NotFoundException as e:
        return jsonify({'message': str(e)}), 404
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

@user_management_bp.route('/users', methods=['POST'])
@roles_required ('Admin', 'Manager')
@sanitize_request_data
@limiter.limit("20 per minute")
def create_user():
    """Create a new user with full audit logging."""
    try:
        # CSRF token validation is handled by rbac_check middleware
        user_data = request.get_json()
        if not user_data:
            raise ValidationException("Request data is required")

        # User data is already sanitized by middleware
        new_user = UserService.create_user(user_data)

        # Log admin action with full context
        security_logger.info({
            'event': 'ADMIN_CREATE_USER',
            'admin_id': g.user['id'],
            'admin_email': g.user['email'],
            'created_user_id': new_user['id'],
            'created_user_email': new_user['email'],
            'created_user_role': new_user['role'],
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'request_id': getattr(g, 'request_id', 'unknown')
        })

        return jsonify({
            'message': 'User created successfully',
            'user': new_user
        }), 201

    except ValidationException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_management_bp.route('/users/<int:user_id>', methods=['PUT'])
@api_resource_handler(User, schema=UpdateUserSchema(), check_ownership=False)
@roles_required ('Admin', 'Manager', 'Support')
@sanitize_request_data
@limiter.limit("20 per minute")
def update_user(user_id):
    """Update user with full audit logging."""
    try:
        updated_user = UserService.update_user(user_id, g.validated_data)

        # Log admin action
        security_logger.info({
            'event': 'ADMIN_UPDATE_USER',
            'admin_id': g.user['id'],
            'admin_email': g.user['email'],
            'updated_user_id': user_id,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'request_id': getattr(g, 'request_id', 'unknown')
        })

        return jsonify({
            'message': 'User updated successfully',
            'user': updated_user
        })

    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except ValidationException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@user_management_bp.route('/<int:user_id>', methods=['DELETE'])
@api_resource_handler(User, check_ownership=False)
@roles_required ('Admin', 'Manager', 'Support', 'Deleter')
@sanitize_request_data
def delete_user(user_id):
    hard_delete = request.args.get('hard', 'false').lower() == 'true'
    if hard_delete:
        if UserService.hard_delete_user(user_id):
            security_logger.warning({
                'event': 'ADMIN_HARD_DELETE_USER',
                'admin_id': g.user['id'],
                'admin_email': g.user['email'],
                'deleted_user_id': user_id,
                'ip_address': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'request_id': getattr(g, 'request_id', 'unknown')
            })
            return jsonify({"message": "User permanently deleted"})
        return jsonify({"error": "User not found"}), 404
    else:
        if UserService.soft_delete_user(user_id):
            return jsonify({"message": "User soft-deleted successfully"})
        return jsonify({"error": "User not found"}), 404
        
@user_management_bp.route('/<int:user_id>/restore', methods=['PUT'])
@api_resource_handler(User, check_ownership=False)
@roles_required('Admin', 'Manager', 'Support')
def restore_user(user_id):
    if UserService.restore_user(user_id):
        return jsonify({"message": "User restored successfully"})
    return jsonify({"error": "User not found"}), 404

@user_management_bp.route('/users/<int:user_id>/roles', methods=['POST'])
@roles_required('Admin', 'Manager')
@limiter.limit("30 per minute")
def assign_role_to_user(user_id):
    """
    Assigns a role to a user. RBAC implementation.
    """
    data = request.get_json()
    role_name = InputSanitizer.sanitize_input(data.get('role_name'))
    
    if not role_name:
        return jsonify({"error": "Role name is required."}), 400

    user = User.query.get_or_404(user_id)
    RBACService.assign_role_to_user(user, role_name)
    
    AuditLogService.log_action(
        user_id=current_user.id,
        action='assign_role',
        details=f"Assigned role '{role_name}' to user '{user.email}' (ID: {user_id})."
    )
    
    return jsonify({"message": f"Role '{role_name}' assigned to user {user.email}."})

@user_management_bp.route('/users/<int:user_id>/roles/<string:role_name>', methods=['DELETE'])
@roles_required('Admin', 'Manager')
def remove_role_from_user(user_id, role_name):
    """
    Removes a role from a user. RBAC implementation.
    """
    user = User.query.get_or_404(user_id)
    sanitized_role_name = InputSanitizer.sanitize_input(role_name)
    
    RBACService.remove_role_from_user(user, sanitized_role_name)

    AuditLogService.log_action(
        user_id=current_user.id,
        action='remove_role',
        details=f"Removed role '{sanitized_role_name}' from user '{user.email}' (ID: {user_id})."
    )
    
    return jsonify({"message": f"Role '{sanitized_role_name}' removed from user {user.email}."})
