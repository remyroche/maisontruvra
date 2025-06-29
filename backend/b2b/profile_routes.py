from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.b2b_service import B2BService
from backend.utils.sanitization import sanitize_input
from backend.utils.decorators import staff_required, b2b_user_required, roles_required, permissions_required, b2b_admin_required
from backend.models.b2b_models import B2BUser
from backend.database import db
from backend.tasks import send_email_task

b2b_profile_bp = Blueprint('b2b_profile_bp', __name__, url_prefix='/api/b2b/profile')

@b2b_profile_bp.route('/users', methods=['GET'])
@b2b_user_required
def get_b2b_users():
    """Fetches all users associated with the current user's company account."""
    b2b_user_id = get_jwt_identity()
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

@b2b_profile_bp.route('/users/add', methods=['POST'])
@b2b_admin_required # Only admins of the company can add new users
def add_b2b_user():
    """Adds a new user to the company account."""
    data = request.get_json()
    b2b_user_id = get_jwt_identity()
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
    
    # Send an invitation/welcome email to the new user asynchronously.
    email_context = {
        'inviter_name': current_user.first_name,
        'company_name': current_user.account.name, # Assuming 'account' relationship exists
        'new_user_name': new_user.first_name
    }
    send_email_task.delay(
        recipient=new_user.email,
        subject=f"Invitation to join {current_user.account.name} on Maison Truvrā",
        template_name='emails/b2b_user_invitation.html',
        context=email_context
    )
    
    return jsonify({"message": "User added successfully.", "user_id": new_user.id}), 201

@b2b_profile_bp.route('/users/remove', methods=['POST'])
@b2b_admin_required
def remove_b2b_user():
    """Removes a user from the company account."""
    data = request.get_json()
    user_to_remove_id = data.get('user_id')
    
    b2b_user_id = get_jwt_identity()
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
@b2b_user_required
def add_b2b_address():
    user_id = get_jwt_identity()
    data = sanitize_input(request.get_json())
    # Assuming B2BService has a method to handle address creation for a user
    address = B2BService.add_address_for_user(user_id, data)
    return jsonify(address.to_dict()), 201

@b2b_profile_bp.route('/address/<int:address_id>', methods=['PUT'])
@b2b_user_required
def update_b2b_address(address_id):
    user_id = get_jwt_identity()
    data = sanitize_input(request.get_json())
    # Assuming B2BService can update an address, checking ownership via user_id
    address = B2BService.update_address_for_user(address_id, user_id, data)
    return jsonify(address.to_dict())

@b2b_profile_bp.route('/address/<int:address_id>', methods=['DELETE'])
@b2b_user_required
def delete_b2b_address(address_id):
    user_id = get_jwt_identity()
    # Assuming B2BService can delete an address, checking ownership via user_id
    B2BService.delete_address_for_user(address_id, user_id)
    return jsonify({'message': 'Address deleted'})

@b2b_profile_bp.route('/invoices', methods=['GET'])
@b2b_user_required
def get_b2b_invoices():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    try:
        invoices_pagination = B2BService.get_b2b_invoices_paginated(user_id, page, per_page)
        return jsonify({
            "items": [invoice.to_dict() for invoice in invoices_pagination.items],
            "total": invoices_pagination.total,
            "pages": invoices_pagination.pages,
            "current_page": invoices_pagination.page
        })
    except Exception as e:
        return jsonify(error=str(e)), 500

@b2b_profile_bp.route('/cart', methods=['GET'])
@b2b_user_required
def get_b2b_cart():
    user_id = get_jwt_identity()
    try:
        cart = B2BService.get_b2b_cart(user_id)
        return jsonify(cart.to_dict())
    except Exception as e:
        return jsonify(error=str(e)), 500

@b2b_profile_bp.route('/orders/create', methods=['POST'])
@b2b_user_required
def create_b2b_order():
    user_id = get_jwt_identity()
    data = request.get_json()
    try:
        order = B2BService.create_b2b_order(user_id, data)
        return jsonify(order_id=order.id, message="B2B Order created successfully"), 201
    except Exception as e:
        return jsonify(error=str(e)), 500
