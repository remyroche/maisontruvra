from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from backend.services.user_service import UserService
from backend.services.mfa_service import MfaService
from backend.services.address_service import AddressService
from backend.utils.sanitization import sanitize_input
from backend.models.user_models import User
from backend.database import db
from backend.services.email_service import EmailService
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User, Address
from services.user_service import UserService
from services.mfa_service import MFAService
from utils.auth_helpers import send_password_change_email
from utils.sanitization import sanitize_input

account_bp = Blueprint('account', __name__)
user_service = UserService()
mfa_service = MFAService()



@account_bp.route('/', methods=['GET'])
@login_required
def get_account_details():
    return jsonify(current_user.to_user_dict())

@account_bp.route('/update', methods=['POST'])
@login_required
def update_account():
    data = sanitize_input(request.get_json())
    updated_user = user_service.update_user(current_user.id, data)
    return jsonify(updated_user.to_user_dict())

    
@admin_user_management_bp.route('/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    user = user_service.get_user_by_id(user_id)
    if user:
        return jsonify(user.to_admin_dict())
    return jsonify({'error': 'User not found'}), 404

@products_bp.route('/<string:slug>', methods=['GET'])
def get_product(slug):
    sanitized_slug = sanitize_input(slug)
    product = product_service.get_product_by_slug(sanitized_slug)
    if product and product.is_active:
        return jsonify(product.to_public_dict(include_variants=True, include_reviews=True))
    return jsonify({'error': 'Product not found'}), 404

# backend/orders/routes.py
@orders_bp.route('/<int:order_id>', methods=['GET'])
@login_required
def get_order_details(order_id):
    order = order_service.get_order_by_id_for_user(order_id, current_user.id)
    if order:
        return jsonify(order.to_user_dict())
    return jsonify({'error': 'Order not found'}), 404




# GET current user's profile
@account_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get the profile information for the currently authenticated user.
    """
    user_id = get_jwt_identity()
    user = UserService.get_user_by_id(user_id)
    if not user:
        return jsonify(status="error", message="User not found"), 404
    
    return jsonify(status="success", data=user.to_dict()), 200

    
# UPDATE current user's profile
@account_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update the profile information for the currently authenticated user.
    """
    user_id = get_jwt_identity()
    data = sanitize_input(request.get_json())
    if not data:
        return jsonify(status="error", message="Invalid or missing JSON body"), 400
    
    sanitized_data = sanitize_input(data)

    # For security, certain fields should not be updatable via this endpoint.
    sanitized_data.pop('password', None)
    sanitized_data.pop('email', None) # Email changes should have a separate, verified flow.
    sanitized_data.pop('role', None) # Role should only be changed by an admin.
    sanitized_data.pop('is_mfa_enabled', None)

    try:
        updated_user = UserService.update_user(user_id, sanitized_data)
        if not updated_user:
             return jsonify(status="error", message="User not found or update failed"), 404
        return jsonify(status="success", data=updated_user.to_dict()), 200
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred while updating the profile."), 500

# UPDATE current user's password
@account_bp.route('/password', methods=['PUT'])
@jwt_required()
def update_password():
    """
    Update the password for the currently authenticated user.
    Requires the old password for verification.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data or 'old_password' not in data or 'new_password' not in data:
        return jsonify(status="error", message="Both old_password and new_password are required."), 400

    old_password = data['old_password'] # Do not sanitize passwords
    new_password = data['new_password']

    try:
        # The service should handle verification of the old password
        if not check_password_hash(current_user.password_hash, old_password):
            return jsonify({'error': 'Invalid old password'}), 400
        else:
            return jsonify(status="error", message="Invalid current password or failed to update."), 400
    
    EmailService.send_security_alert(user, "Votre mot de passe a été modifié")

    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred."), 500

# GET current user's order history
@account_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_order_history():
    """
    Get the order history for the currently authenticated user.
    """
    user_id = get_jwt_identity()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        # Assumes a service method to get orders for a specific user
        orders_pagination = UserService.get_user_orders_paginated(user_id, page=page, per_page=per_page)
        
        return jsonify({
            "status": "success",
            "data": [order.to_dict_for_user() for order in orders_pagination.items], # Use a user-safe serializer
            "total": orders_pagination.total,
            "pages": orders_pagination.pages,
            "current_page": orders_pagination.page
        }), 200
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An error occurred while fetching order history."), 500

# --- NEW: 2FA Management Routes ---

@account_bp.route('/2fa/setup', methods=['POST'])
@jwt_required()
def setup_2fa():
    """Initiates the 2FA setup process for the current user."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.is_mfa_enabled:
        return jsonify(status="error", message="2FA is already enabled."), 400

    secret = MfaService.generate_secret()
    user.mfa_secret = secret  # Temporarily store the secret
    db.session.commit()
    
    uri = MfaService.get_provisioning_uri(user.email, secret)
    qr_code_uri = MfaService.generate_qr_code(uri)
    
    return jsonify(status="success", data={"qr_code": qr_code_uri, "secret": secret}), 200


@account_bp.route('/2fa/verify', methods=['POST'])
@jwt_required()
def verify_2fa():
    """Verifies the token and enables 2FA for the user."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    token = sanitize_input(data.get('token'))
    
    if not user.mfa_secret:
        return jsonify(status="error", message="No 2FA setup process was initiated."), 400
        
    if MfaService.verify_token(user.mfa_secret, token):
        user.is_mfa_enabled = True
        db.session.commit()
        return jsonify(status="success", message="2FA enabled successfully."), 200
    else:
        return jsonify(status="error", message="Invalid 2FA token."), 400


@account_bp.route('/2fa/disable', methods=['POST'])
@jwt_required()
def disable_2fa():
    """Disables 2FA for the user, requires a valid token to do so."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    token = sanitize_input(data.get('token'))

    if not user.is_mfa_enabled:
        return jsonify(status="error", message="2FA is not currently enabled."), 400

    if MfaService.verify_token(user.mfa_secret, token):
        user.is_mfa_enabled = False
        user.mfa_secret = None # Clear the secret
        db.session.commit()
        EmailService.send_security_alert(user, "L'authentification à deux facteurs (2FA) a été désactivée")
        return jsonify(status="success", message="2FA disabled successfully."), 200
    else:
        return jsonify(status="error", message="Invalid 2FA token."), 400

# --- NEW: Address Book Management Routes ---

@account_bp.route('/addresses', methods=['GET'])
@jwt_required()
def get_addresses():
    addresses = Address.query.filter_by(user_id=current_user.id).all()
    return jsonify([address.to_dict() for address in addresses])

@account_bp.route('/addresses', methods=['POST'])
@jwt_required()
def add_address():
    user_id = get_jwt_identity()
    data = sanitize_input(request.get_json())
    try:
        new_address = AddressService.add_address_for_user(user_id, data)
        return jsonify(status="success", data=new_address.to_dict()), 201
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400 # Catches the 4-address limit error

@account_bp.route('/addresses/<int:address_id>', methods=['PUT'])
@jwt_required()
def update_address(address_id):
    user_id = get_jwt_identity()
    data = sanitize_input(request.get_json())
    updated_address = AddressService.update_address(address_id, user_id, data)
    return jsonify(status="success", data=updated_address.to_dict()), 200

@account_bp.route('/addresses/<int:address_id>', methods=['DELETE'])
@jwt_required()
def delete_address(address_id):
    user_id = get_jwt_identity()
    AddressService.delete_address(address_id, user_id)
    return jsonify(status="success", message="Address deleted successfully."), 200

