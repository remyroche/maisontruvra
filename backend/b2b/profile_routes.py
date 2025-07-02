from flask import Blueprint, request, jsonify, session, g, redirect, url_for, flash, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.b2b_service import B2BService
from backend.utils.input_sanitizer import InputSanitizer
from backend.utils.decorators import staff_required, b2b_user_required, roles_required, permissions_required, b2b_admin_required, api_resource_handler
from backend.models.user_models import User
from backend.models.address_models import Address
from backend.schemas import UserSchema, AddressSchema
from backend.extensions import db
from backend.tasks import send_email_task
from backend.utils.decorators import b2b_user_required
from flask_login import current_user
from backend.models import db, User, Company
from backend.services.b2b_service import B2BService
from backend.utils.decorators import login_required

b2b_profile_bp = Blueprint('b2b_profile_bp', __name__, url_prefix='/api/b2b/profile')
b2b_service = B2BService()
user_service = UserService()


@b2b_profile_bp.route('/users', methods=['GET'])
@login_required
@b2b_user_required
def get_b2b_users():
    """Récupère tous les utilisateurs associés à l'entreprise de l'utilisateur actuel."""
    if not current_user.company_id:
        return jsonify({"error": "L'utilisateur n'est pas associé à une entreprise."}), 400

    users = User.query.filter_by(company_id=current_user.company_id).all()
    
    user_list = [{
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'roles': [role.name.value for role in user.roles] # Utilise la relation de rôles
    } for user in users]
    
    return jsonify(user_list)

@b2b_profile_bp.route('/users/add', methods=['POST'])
@jwt_required()
@api_resource_handler(model=B2BUser, request_schema=B2BUserInviteSchema, response_schema=B2BUserSchema, log_action=True)
def add_b2b_user():
    """
    Invites a new user to the B2B account.
    The decorator handles input validation and response serialization.
    """
    admin_user_id = get_jwt_identity()
    invited_user = B2BService.invite_user(admin_user_id, g.validated_data)
    return invited_user

@b2b_profile_bp.route('/users/remove', methods=['POST'])
@login_required
@b2b_admin_required
def remove_b2b_user():
    """Supprime un utilisateur du compte de l'entreprise."""
    data = request.get_json()
    user_to_remove_id = data.get('user_id')
    
    if not user_to_remove_id:
        return jsonify({"error": "L'ID de l'utilisateur est requis."}), 400

    if not current_user.company_id:
        return jsonify({"error": "L'utilisateur admin n'est pas associé à une entreprise."}), 400

    user_to_remove = user_service.get_user_by_id(user_to_remove_id)
    
    # S'assurer que l'utilisateur existe et appartient à la même entreprise
    if not user_to_remove or user_to_remove.company_id != current_user.company_id:
        return jsonify({"error": "Utilisateur non trouvé ou ne faisant pas partie de cette entreprise."}), 404
        
    # Empêcher un admin de se supprimer lui-même
    if user_to_remove.id == current_user.id:
        return jsonify({"error": "Vous ne pouvez pas vous supprimer vous-même du compte."}), 403

    try:
        db.session.delete(user_to_remove)
        db.session.commit()
        return jsonify({"message": "Utilisateur supprimé avec succès."}), 200
    except Exception as e:
        db.session.rollback()
        # Log l'erreur pour le débogage
        return jsonify({"error": "Échec de la suppression de l'utilisateur."}), 500


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
def edit_profile():
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


@b2b_profile_bp.route('/company/profile')
@api_resource_handler(
    model=Company,
    response_schema=UserSchema,
    ownership_exempt_roles=[],  # Only the user themselves can access
    cache_timeout=0,  # No caching for company profiles
    log_action=True
)
@b2b_user_required
def company_profile():
    """Affiche le profil de l'entreprise de l'utilisateur B2B."""
    # La logique est correcte car elle utilise `current_user.company`
    company = current_user.company
    if not company:
        flash("Profil d'entreprise non trouvé.", 'warning')
        return redirect(url_for('b2b_dashboard_bp.dashboard'))
    return render_template('b2b/company_profile.html', company=company)


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
