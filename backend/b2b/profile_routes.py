from flask import Blueprint, request, jsonify, session, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.b2b_service import B2BService
from backend.utils.input_sanitizer import InputSanitizer
from backend.utils.decorators import staff_required, b2b_user_required, roles_required, permissions_required, b2b_admin_required, api_resource_handler
from backend.models.user_models import User
from backend.models.address_models import Address
from backend.schemas import UserSchema, AddressSchema
from backend.extensions import db
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
    
# GET the B2B user's profile
@b2b_profile_bp.route('/', methods=['GET'])
@api_resource_handler(
    model=User,
    response_schema=UserSchema,
    ownership_exempt_roles=[],  # Only the user themselves can access
    cache_timeout=0,  # No caching for user profiles
    log_action=True
)
@b2b_user_required
@jwt_required()
def get_b2b_profile():
    """
    Get the profile of the currently authenticated B2B user.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.user_type.value != 'B2B':
        return None  # Will be handled by decorator as 404
    return user

# UPDATE the B2B user's profile
@b2b_profile_bp.route('/', methods=['PUT'])
@api_resource_handler(
    model=User,
    request_schema=UserSchema,
    response_schema=UserSchema,
    ownership_exempt_roles=[],  # Only the user themselves can update
    cache_timeout=0,  # No caching for user profiles
    log_action=True
)
@b2b_user_required
@jwt_required()
def update_b2b_profile():
    """
    Update the profile information for the authenticated B2B user.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.user_type.value != 'B2B':
        return None  # Will be handled by decorator as 404
    
    # Update user with validated data from g.validated_data
    for key, value in g.validated_data.items():
        if hasattr(user, key) and key not in ['vat_number', 'status']:  # Exclude sensitive fields
            setattr(user, key, value)
    
    return user


@b2b_profile_bp.route('/address', methods=['POST'])
@api_resource_handler(
    model=Address,
    request_schema=AddressSchema,
    response_schema=AddressSchema,
    ownership_exempt_roles=[],  # Only the user themselves can create
    cache_timeout=0,  # No caching for addresses
    log_action=True
)
@b2b_user_required
@jwt_required()
def add_b2b_address():
    """Create a new address for the authenticated B2B user."""
    user_id = get_jwt_identity()
    
    # Create new address with validated data
    address = Address()
    address.user_id = user_id
    for key, value in g.validated_data.items():
        if hasattr(address, key):
            setattr(address, key, value)
    
    db.session.add(address)
    return address

@b2b_profile_bp.route('/address/<int:address_id>', methods=['PUT'])
@api_resource_handler(
    model=Address,
    request_schema=AddressSchema,
    response_schema=AddressSchema,
    ownership_exempt_roles=[],  # Only the owner can update
    cache_timeout=0,  # No caching for addresses
    log_action=True
)
@b2b_user_required
@jwt_required()
def update_b2b_address(address_id):
    """Update an existing address for the authenticated B2B user."""
    # Address is already fetched and validated by decorator
    address = g.target_object
    
    # Update address with validated data
    for key, value in g.validated_data.items():
        if hasattr(address, key):
            setattr(address, key, value)
    
    return address

@b2b_profile_bp.route('/address/<int:address_id>', methods=['DELETE'])
@api_resource_handler(
    model=Address,
    ownership_exempt_roles=[],  # Only the owner can delete
    cache_timeout=0,  # No caching for addresses
    log_action=True
)
@b2b_user_required
@jwt_required()
def delete_b2b_address(address_id):
    """Delete an address for the authenticated B2B user."""
    # Address is already fetched and validated by decorator
    address = g.target_object
    db.session.delete(address)
    return None  # Decorator will handle the delete response

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
