from flask import Blueprint, jsonify, request
from backend.services.b2b_service import B2BService
from backend.utils.decorators import staff_required, roles_required, permissions_required
from backend.models.enums import B2BRequestStatus
from backend.services.b2b_service import B2BService
from backend.services.exceptions import B2BAccountExistsError, UserNotFoundError, NotFoundException


b2b_management_bp = Blueprint('b2b_management', __name__, url_prefix='/api/admin/b2b')

@b2b_management_bp.route('/accounts', methods=['GET'])
@roles_required ('Admin', 'Manager', 'Support')
def get_b2b_accounts():
    """Returns a list of all B2B accounts with their status and tier."""
    # This needs to be implemented to fetch all B2B users and their tiers
    b2b_users = B2BService.get_all_b2b_users_with_details() # Assumes a method in B2BService
    return jsonify([user.to_dict() for user in b2b_users]), 200


@b2b_management_bp.route('/accounts/<int:account_id>/approve', methods=['PUT'])
@roles_required ('Admin', 'Manager', 'Support')
def approve_b2b_account(b2b_user_id):
    """Approves a B2B account."""
    try:
        b2b_user = B2BService.approve_b2b_account(b2b_user_id)
        if not b2b_user:
            return jsonify({'message': 'B2B account not found'}), 404
        return jsonify({'message': 'B2B account approved successfully'}), 200
    except NotFoundException as e:
        return jsonify({'message': str(e)}), 404
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500
        
@b2b_management_bp.route('/accounts/<int:account_id>', methods=['PUT'])
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


# Tier Management
@b2b_management_bp.route('/tiers', methods=['POST'])
@admin_required
def create_tier():
    """Creates a new B2B pricing tier."""
    data = request.get_json()
    if not data or 'name' not in data or 'discount_percentage' not in data:
        return jsonify({'message': 'Missing required fields'}), 400
    
    try:
        tier = B2BService.create_tier(
            name=data['name'],
            discount_percentage=Decimal(data['discount_percentage']),
            minimum_spend=Decimal(data.get('minimum_spend')) if data.get('minimum_spend') else None
        )
        return jsonify({'message': 'Tier created successfully', 'tier_id': tier.id}), 201
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

@b2b_management_bp.route('/tiers', methods=['GET'])
@admin_required
def get_all_tiers():
    """Retrieves all B2B pricing tiers."""
    tiers = B2BService.get_all_tiers()
    return jsonify([{
        'id': tier.id,
        'name': tier.name,
        'discount_percentage': str(tier.discount_percentage),
        'minimum_spend': str(tier.minimum_spend) if tier.minimum_spend else None
    } for tier in tiers]), 200

@b2b_management_bp.route('/tiers/<int:tier_id>', methods=['PUT'])
@admin_required
def update_tier(tier_id):
    """Updates an existing B2B pricing tier."""
    data = request.get_json()
    try:
        tier = B2BService.update_tier(
            tier_id,
            name=data.get('name'),
            discount_percentage=Decimal(data['discount_percentage']) if data.get('discount_percentage') else None,
            minimum_spend=Decimal(data.get('minimum_spend')) if data.get('minimum_spend') else None
        )
        if not tier:
            return jsonify({'message': 'Tier not found'}), 404
        return jsonify({'message': 'Tier updated successfully'}), 200
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

@b2b_management_bp.route('/users/<int:b2b_user_id>/assign-tier', methods=['POST'])
@admin_required
def assign_tier_to_user(b2b_user_id):
    """Assigns a tier to a B2B user."""
    data = request.get_json()
    if not data or 'tier_id' not in data:
        return jsonify({'message': 'tier_id is required'}), 400
    
    try:
        b2b_user = B2BService.assign_tier_to_b2b_user(b2b_user_id, data['tier_id'])
        if not b2b_user:
            return jsonify({'message': 'B2B user or tier not found'}), 404
        return jsonify({'message': f'Tier assigned to {b2b_user.company_name} successfully'}), 200
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

