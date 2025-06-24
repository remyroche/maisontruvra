from flask import Blueprint, request, jsonify
from backend.services.b2b_service import B2BService  # Assumed service
from backend.utils.sanitization import sanitize_input
from ..utils.decorators import admin_required, staff_required, roles_required, permissions_required
from ..utils.decorators import log_admin_action
from utils.sanitization import sanitize_input
from services.user_service import UserService
from ..utils.decorators import log_admin_action

b2b_management_bp = Blueprint('b2b_management_bp', __name__, url_prefix='/admin/b2b')
user_service = UserService()

# READ all B2B accounts (paginated with filtering)
@b2b_management_bp.route('/', methods=['GET'])
@permissions_required('MANAGE_B2B_ACCOUNTS')
@log_admin_action
@roles_required ('Admin')
@admin_required
def get_b2b_accounts():
    """
    Get a paginated list of B2B accounts.
    Query Params:
    - page: The page number.
    - per_page: The number of accounts per page.
    - status: Filter by account status (e.g., 'pending', 'approved', 'rejected').
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = sanitize_input(request.args.get('status'))
        sort_by = sanitize_input(request.args.get('sort_by', 'company_name'))
        sort_direction = sanitize_input(request.args.get('sort_direction', 'asc'))
        
        filters = {'status': status} if status else {}
        
        accounts_pagination = B2BService.get_all_b2b_accounts_paginated(page=page, per_page=per_page, filters=filters)
        
        return jsonify({
            "status": "success",
            "data": [account.to_dict() for account in accounts_pagination.items],
            "total": accounts_pagination.total,
            "pages": accounts_pagination.pages,
            "current_page": accounts_pagination.page
        }), 200
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred while fetching B2B accounts."), 500


@admin_b2b_bp.route('/approve/<int:account_id>', methods=['POST'])
@jwt_required()
@log_admin_action
@roles_required ('Admin')
@admin_required
def approve_b2b_account(account_id):
    # Assuming this service returns the primary user of the approved account
    approved_user = B2BAuthService.approve_account(account_id)
    
    # --- Send "Account Approved" Email ---
    EmailService.send_b2b_account_approved_email(approved_user)
    
    return jsonify({"message": "B2B account approved and user notified."}), 200


# READ a single B2B account
@b2b_management_bp.route('/<int:account_id>', methods=['GET'])
@permissions_required('MANAGE_B2B_ACCOUNTS')
@log_admin_action
@roles_required ('Admin')
@admin_required
def get_b2b_account(account_id):
    """
    Get details for a single B2B account.
    """
    account = B2BService.get_b2b_account_by_id(account_id)
    if account:
        return jsonify(status="success", data=account.to_dict()), 200
    return jsonify(status="error", message="B2B account not found"), 404

# UPDATE a B2B account (e.g., approve, reject, update details)
@b2b_management_bp.route('/<int:account_id>', methods=['PUT'])
@permissions_required('MANAGE_B2B_ACCOUNTS')
@log_admin_action
@roles_required ('Admin')
@admin_required
def update_b2b_account(account_id):
    """
    Update a B2B account's status or other details.
    """
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Invalid or missing JSON body"), 400

    if not B2BService.get_b2b_account_by_id(account_id):
        return jsonify(status="error", message="B2B account not found"), 404
        
    sanitized_data = sanitize_input(data)

    try:
        updated_account = B2BService.update_b2b_account(account_id, sanitized_data)
        return jsonify(status="success", data=updated_account.to_dict()), 200
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="Failed to update B2B account."), 500

# DELETE a B2B account
@b2b_management_bp.route('/<int:account_id>', methods=['DELETE'])
@permissions_required('MANAGE_B2B_ACCOUNTS')
@log_admin_action
@roles_required ('Admin')
@admin_required
def delete_b2b_account(account_id):
    """
    Delete a B2B account.
    """
    if not B2BService.get_b2b_account_by_id(account_id):
        return jsonify(status="error", message="B2B account not found"), 404
    try:
        B2BService.delete_b2b_account(account_id)
        return jsonify(status="success", message="B2B account deleted successfully"), 200
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="Failed to delete B2B account."), 500


