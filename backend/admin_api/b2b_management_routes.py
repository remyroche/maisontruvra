from flask import Blueprint, jsonify, request
from backend.services.b2b_service import B2BService
from backend.auth.permissions import admin_required, staff_required, roles_required, permissions_required
from ..utils.decorators import log_admin_action
from backend.models.enums import B2BAccountStatus

b2b_management_bp = Blueprint('b2b_management', __name__, url_prefix='/api/admin/b2b')

@b2b_management_bp.route('/accounts', methods=['GET'])
@admin_required
@log_admin_action
@roles_required ('Admin', 'Manager', 'Support')
def get_b2b_accounts():
    """
    Retrieves all B2B accounts, with optional filtering by status.
    ---
    tags:
      - Admin B2B Management
    parameters:
      - in: query
        name: status
        schema:
          type: string
        description: Filter accounts by status (e.g., 'pending', 'approved', 'rejected').
    security:
      - cookieAuth: []
    responses:
      200:
        description: A list of B2B accounts.
    """
    status_filter = request.args.get('status')
    accounts = B2BService.get_all_b2b_accounts(status_filter=status_filter)
    return jsonify([acc.to_dict() for acc in accounts])

@b2b_management_bp.route('/accounts/<int:account_id>/approve', methods=['PUT'])
@admin_required
@log_admin_action
@roles_required ('Admin', 'Manager', 'Support')
def approve_b2b_account(account_id):
    """
    Approves a pending B2B account.
    ---
    tags:
      - Admin B2B Management
    parameters:
      - in: path
        name: account_id
        required: true
        schema:
          type: integer
    security:
      - cookieAuth: []
    responses:
      200:
        description: B2B account approved successfully.
      404:
        description: Account not found.
    """
    account = B2BService.update_b2b_account_status(account_id, B2BAccountStatus.APPROVED)
    if not account:
        return jsonify({"error": "Account not found"}), 404
    # You might want to trigger a confirmation email here
    return jsonify(account.to_dict())

@b2b_management_bp.route('/accounts/<int:account_id>', methods=['PUT'])
@admin_required
@log_admin_action
@roles_required ('Admin', 'Manager', 'Support')
def update_b2b_account(account_id):
    """
    Updates details of a B2B account.
    ---
    tags:
      - Admin B2B Management
    parameters:
      - in: path
        name: account_id
        required: true
        schema:
          type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            status:
              type: string
              description: The new status for the account.
    security:
      - cookieAuth: []
    responses:
      200:
        description: Account updated successfully.
      404:
        description: Account not found.
    """
    data = request.get_json()
    account = B2BService.update_b2b_account(account_id, data)
    if not account:
        return jsonify({"error": "Account not found"}), 404
    return jsonify(account.to_dict())

@b2b_management_bp.route('/accounts/<int:account_id>', methods=['DELETE'])
@admin_required
@log_admin_action
@roles_required ('Admin', 'Manager', 'Support')
def delete_b2b_account(account_id):
    """
    Deletes a B2B account.
    ---
    tags:
      - Admin B2B Management
    parameters:
      - in: path
        name: account_id
        required: true
        schema:
          type: integer
    security:
      - cookieAuth: []
    responses:
      200:
        description: Account deleted successfully.
      404:
        description: Account not found.
    """
    if B2BService.delete_b2b_account(account_id):
        return jsonify({"message": "Account deleted successfully"})
    return jsonify({"error": "Account not found"}), 404

