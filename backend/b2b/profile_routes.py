from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.b2b_service import B2BService
from backend.utils.sanitization import sanitize_input
from backend.auth.permissions import b2b_user_required

b2b_profile_bp = Blueprint('b2b_profile_bp', __name__, url_prefix='/api/b2b/profile')

@b2b_bp.route('/api/b2b/users', methods=['GET'])
@b2b_login_required
def get_b2b_users():
    """Fetches all users associated with the current user's company account."""
    b2b_user_id = session.get('b2b_user_id')
    current_user = db.session.get(B2BUser, b2b_user_id)
    
    users = B2BUser.query.filter_by(account_id=current_user.account_id).all()
    user_list = [{
        'id': user.id, 
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email, 
        'role': user.role
    } for user in users]
    
    return jsonify(user_list)

@b2b_bp.route('/api/b2b/users/add', methods=['POST'])
@b2b_admin_required # Only admins of the company can add new users
def add_b2b_user():
    """Adds a new user to the company account."""
    data = request.get_json()
    b2b_user_id = session.get('b2b_user_id')
    current_user = db.session.get(B2BUser, b2b_user_id)
    
    # Check for existing user with the same email
    existing_user = B2BUser.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"error": "User with this email already exists."}), 409

    new_user = B2BUser(
        account_id=current_user.account_id,
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        role=data.get('role', 'member') # Default to 'member' role
    )
    new_user.set_password(data['password'])
    
    db.session.add(new_user)
    db.session.commit()
    
    # TODO: Send an invitation/welcome email to the new user.
    
    return jsonify({"message": "User added successfully.", "user_id": new_user.id}), 201

@b2b_bp.route('/api/b2b/users/remove', methods=['POST'])
@b2b_admin_required
def remove_b2b_user():
    """Removes a user from the company account."""
    data = request.get_json()
    user_to_remove_id = data.get('user_id')
    
    b2b_user_id = session.get('b2b_user_id')
    current_user = db.session.get(B2BUser, b2b_user_id)

    user_to_remove = db.session.get(B2BUser, user_to_remove_id)
    
    # Ensure the user exists and belongs to the same company
    if not user_to_remove or user_to_remove.account_id != current_user.account_id:
        return jsonify({"error": "User not found or not part of this account."}), 404
        
    # Prevent the admin from removing themselves
    if user_to_remove.id == current_user.id:
        return jsonify({"error": "You cannot remove yourself from the account."}), 403

    db.session.delete(user_to_remove)
    db.session.commit()
    
    return jsonify({"message": "User removed successfully."}), 200
    
# GET the B2B user's company profile
@b2b_profile_bp.route('/', methods=['GET'])
@b2b_user_required
def get_b2b_profile():
    """
    Get the company profile associated with the currently authenticated B2B user.
    """
    user_id = get_jwt_identity()
    try:
        # Assumes the service can find the company profile linked to the user
        profile = B2BService.get_company_profile_by_user(user_id)
        if not profile:
            return jsonify(status="error", message="B2B profile not found for this user."), 404
        
        return jsonify(status="success", data=profile.to_dict()), 200
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An error occurred while fetching the B2B profile."), 500

# UPDATE the B2B user's company profile
@b2b_profile_bp.route('/', methods=['PUT'])
@b2b_user_required
def update_b2b_profile():
    """
    Update the company profile information for the authenticated B2B user.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Invalid or missing JSON body"), 400

    sanitized_data = sanitize_input(data)
    
    # Remove sensitive fields that should not be changed here
    sanitized_data.pop('vat_number', None)
    sanitized_data.pop('status', None) # Status should only be changed by an admin

    try:
        updated_profile = B2BService.update_company_profile_by_user(user_id, sanitized_data)
        if not updated_profile:
            return jsonify(status="error", message="B2B Profile not found or update failed"), 404
        return jsonify(status="success", data=updated_profile.to_dict()), 200
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred while updating the B2B profile."), 500


@b2b_profile_bp.route('/address', methods=['POST'])
@b2b_required
def add_b2b_address():
    data = sanitize_input(request.get_json())
    address = b2b_user_service.add_address(current_user.id, data)
    return jsonify(address.to_dict()), 201

@b2b_profile_bp.route('/address/<int:address_id>', methods=['PUT'])
@b2b_required
def update_b2b_address(address_id):
    data = sanitize_input(request.get_json())
    address = b2b_user_service.update_address(address_id, data, current_user.id)
    return jsonify(address.to_dict())

@b2b_profile_bp.route('/address/<int:address_id>', methods=['DELETE'])
@b2b_required
def delete_b2b_address(address_id):
    b2b_user_service.delete_address(address_id, current_user.id)
    return jsonify({'message': 'Address deleted'})

