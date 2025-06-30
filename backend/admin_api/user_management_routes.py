from flask import Blueprint, request, jsonify, g
from backend.services.user_service import UserService
from backend.services.exceptions import NotFoundException, ValidationException, UnauthorizedException
from backend.middleware import sanitize_request_data
from backend.utils.input_sanitizer import InputSanitizer
from backend.services.audit_log_service import AuditLogService
from backend.utils.csrf_protection import CSRFProtection
import logging
from backend.utils.decorators import staff_required, roles_required, permissions_required
from backend.services.discount_service import DiscountService

logger = logging.getLogger(__name__)
security_logger = logging.getLogger('security')

user_management_bp = Blueprint('user_management', __name__)

@user_management_bp.route('/users', methods=['GET'])
@roles_required ('Admin', 'Manager')
@sanitize_request_data
def get_users():
    """Get paginated list of users with proper N+1 optimization."""
    try:
        # Sanitized request args are already available due to middleware
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)  # Max 100 per page
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'

        filters = {}
        if request.args.get('role'):
            filters['role'] = request.args.get('role')
        if request.args.get('is_active'):
            filters['is_active'] = request.args.get('is_active').lower() == 'true'
        if request.args.get('email'):
            filters['email'] = request.args.get('email')

        result = UserService.get_all_users_paginated(page, per_page, filters, include_deleted)

        # Log admin action
        logger.info({
            'event': 'ADMIN_VIEW_USERS',
            'admin_id': g.user['id'],
            'filters': filters,
            'request_id': getattr(g, 'request_id', 'unknown')
        })

        return jsonify({
            'users': [user.to_dict(context='admin') for user in result.items],
            'total': result.total,
            'pages': result.pages,
            'current_page': result.page,
            'per_page': result.per_page
        })

    except ValidationException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

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
@roles_required ('Admin', 'Manager', 'Support')
@sanitize_request_data
def update_user(user_id):
    """Update user with full audit logging."""
    try:
        update_data = request.get_json()
        if not update_data:
            raise ValidationException("Request data is required")

        updated_user = UserService.update_user(user_id, update_data)

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
@roles_required('Admin', 'Manager', 'Support')
def restore_user(user_id):
    if UserService.restore_user(user_id):
        return jsonify({"message": "User restored successfully"})
    return jsonify({"error": "User not found"}), 404
