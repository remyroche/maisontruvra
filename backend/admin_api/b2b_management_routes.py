from flask import Blueprint, request, jsonify
from backend.services.b2b_service import B2BService
from backend.services.exceptions import NotFoundException
from backend.utils.decorators import staff_required, roles_required, permissions_required
from backend.models.enums import B2BStatus
from decimal import Decimal


b2b_management_bp = Blueprint('b2b_management_api', __name__, url_prefix='/admin/api/b2b')
b2b_service = B2BService()

# --- B2B Account Management ---

@b2b_management_bp.route('/', methods=['GET'])
@roles_required ('Admin', 'Manager', 'Support')
def get_b2b_accounts():
    """Returns a list of all B2B accounts with their company-specific details."""
    accounts = b2b_service.get_all_b2b_accounts()
    return jsonify([acc.to_dict() for acc in accounts])


@b2b_management_bp.route('/<int:b2b_user_id>/status', methods=['PUT'])
@roles_required ('Admin', 'Manager', 'Support')
def update_b2b_account_status(b2b_user_id):
    """Updates a B2B account's status (e.g., "approved", "rejected")."""
    data = request.get_json()
    new_status_str = data.get('status')
    if not new_status_str:
        return jsonify({'message': 'Status is required'}), 400
    
    try:
        new_status = B2BStatus(new_status_str.lower())
    except ValueError:
        valid_statuses = [s.value for s in B2BStatus]
        return jsonify({'message': f'Invalid status. Must be one of: {valid_statuses}'}), 400

    try:
        B2BService.update_b2b_status(b2b_user_id, new_status)
        return jsonify({'message': f'B2B account status updated to {new_status.value}'}), 200
    except NotFoundException as e:
        return jsonify({'message': str(e)}), 404
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500
        
# --- Tier Management ---

@b2b_management_bp.route('/tiers', methods=['POST'])
@roles_required ('Admin', 'Manager')
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
@roles_required ('Admin', 'Manager', 'Support')
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
@roles_required ('Admin', 'Manager')
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
@roles_required ('Admin', 'Manager', 'Support')
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
