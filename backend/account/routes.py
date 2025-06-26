from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from backend.database import db
from backend.models.user_models import User, Address
from backend.services.user_service import UserService
from backend.services.mfa_service import MfaService
from backend.services.address_service import AddressService
from backend.services.email_service import EmailService
from backend.utils.input_sanitizer import InputSanitizer
from backend.utils.auth_helpers import send_password_change_email
from backend.utils.decorators import admin_required # For admin_required decorator
from backend.services.product_service import ProductService # For product_service
from backend.services.order_service import OrderService # For order_service
from backend.admin_api.user_management_routes import admin_user_management_bp
from backend.products.routes import products_bp
from backend.orders.routes import orders_bp
from backend.services.user_service import UserService


account_bp = Blueprint('account_bp', __name__)
user_service = UserService()

mfa_service = MfaService() # Corrected instantiation
address_service = AddressService() # Instantiation
email_service = EmailService() # Instantiation
product_service = ProductService() # Instantiation
order_service = OrderService() # Instantiation



@account_bp.route('/', methods=['GET'])
@login_required
def get_account_details():
    return jsonify(current_user.to_user_dict())


@account_bp.route('/api/account/language', methods=['PUT'])
@login_required
def update_language():
    user_id = session.get('user_id') or session.get('b2b_user_id')
    user_type = session.get('user_type')
    data = request.get_json()
    language = data.get('language')

    if not language:
        return jsonify({"error": "Language is required"}), 400

    try:
        user_service.update_user_language(user_id, language, user_type)
        return jsonify({"message": "Language updated successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@account_bp.route('/update', methods=['POST'])
@login_required
def update_account(): 
    data = InputSanitizer.sanitize_json(request.get_json())
    updated_user = user_service.update_user(current_user.id, data)
    return jsonify(updated_user.to_user_dict())


# --- Misplaced Admin Route (should be in admin_api/user_management_routes.py) ---
@admin_user_management_bp.route('/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    user = user_service.get_user_by_id(user_id)
    if user:
        return jsonify(user.to_admin_dict())
    return jsonify({'error': 'User not found'}), 404

# --- Misplaced Product Route (should be in products/routes.py) ---
@products_bp.route('/<string:slug>', methods=['GET'])
def get_product(slug):
    sanitized_slug = InputSanitizer.sanitize_string(slug)
    product = product_service.get_product_by_slug(sanitized_slug)
    if product and product.is_active:
        return jsonify(product.to_public_dict(include_variants=True, include_reviews=True))
    return jsonify({'error': 'Product not found'}), 404


# --- Misplaced Order Route (should be in orders/routes.py) ---
@orders_bp.route('/<int:order_id>', methods=['GET'])
def get_order_details(order_id): # This route uses Flask-Login's current_user
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
    user = user_service.get_user_by_id(user_id)
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
    data = InputSanitizer.sanitize_json(request.get_json())
    if not data:
        return jsonify(status="error", message="Invalid or missing JSON body"), 400
    
    sanitized_data = InputSanitizer.sanitize_json(data)

    # For security, certain fields should not be updatable via this endpoint.
    sanitized_data.pop('password', None)
    sanitized_data.pop('email', None) # Email changes should have a separate, verified flow.
    sanitized_data.pop('role', None) # Role should only be changed by an admin.
    sanitized_data.pop('two_factor_enabled', None) # Use correct attribute name

    try:
        updated_user = user_service.update_user(user_id, sanitized_data)
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
        user = user_service.get_user_by_id(user_id)
        if not user or not user.check_password(old_password):
            return jsonify({'error': 'Invalid old password'}), 400
        user.set_password(new_password)
        db.session.commit()
        send_password_change_email(user)
        return jsonify(status="success", message="Password updated successfully."), 200

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
        orders_pagination = user_service.get_user_orders_paginated(user_id, page=page, per_page=per_page)
        
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
    
    if user.two_factor_enabled: # Use correct attribute name
        return jsonify(status="error", message="2FA is already enabled."), 400

    secret = mfa_service.generate_secret()
    user.two_factor_secret = secret  # Temporarily store the secret
    db.session.commit()
    
    uri = mfa_service.get_provisioning_uri(user.email, secret)
    qr_code_uri = mfa_service.generate_qr_code(uri)
    
    return jsonify(status="success", data={"qr_code": qr_code_uri, "secret": secret}), 200


@account_bp.route('/2fa/verify', methods=['POST'])
@jwt_required()
def verify_2fa():
    """Verifies the token and enables 2FA for the user."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    token = InputSanitizer.sanitize_string(data.get('token'))
    
    if not user.two_factor_secret: # Use correct attribute name
        return jsonify(status="error", message="No 2FA setup process was initiated."), 400
        
    if mfa_service.verify_token(user.two_factor_secret, token): # Use correct attribute name
        user.two_factor_enabled = True # Use correct attribute name
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
    data = request.get_json() # No need to sanitize the whole dict here
    token = InputSanitizer.sanitize_string(data.get('token')) # Sanitize individual token

    if not user.two_factor_enabled: # Use correct attribute name
        return jsonify(status="error", message="2FA is not currently enabled."), 400

    if mfa_service.verify_token(user.two_factor_secret, token): # Use correct attribute name
        user.two_factor_enabled = False # Use correct attribute name
        user.two_factor_secret = None # Clear the secret
        db.session.commit()
        email_service.send_security_alert(user, "L'authentification à deux facteurs (2FA) a été désactivée")
        return jsonify(status="success", message="2FA disabled successfully."), 200
    else:
        return jsonify(status="error", message="Invalid 2FA token."), 400

# --- NEW: Address Book Management Routes ---

@account_bp.route('/addresses', methods=['GET'])
@jwt_required()
def get_addresses():
    user_id = get_jwt_identity()
    addresses = Address.query.filter_by(user_id=user_id).all()
    return jsonify([address.to_dict() for address in addresses])

@account_bp.route('/addresses', methods=['POST'])
@jwt_required()
def add_address():
    user_id = get_jwt_identity()
    data = InputSanitizer.sanitize_json(request.get_json())
    try:
        new_address = address_service.add_address_for_user(user_id, data)
        return jsonify(status="success", data=new_address.to_dict()), 201
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400 # Catches the 4-address limit error

@account_bp.route('/addresses/<int:address_id>', methods=['PUT'])
@jwt_required()
def update_address(address_id):
    user_id = get_jwt_identity()
    data = InputSanitizer.sanitize_json(request.get_json())
    updated_address = address_service.update_address(address_id, user_id, data)
    return jsonify(status="success", data=updated_address.to_dict()), 200

@account_bp.route('/addresses/<int:address_id>', methods=['DELETE'])
@jwt_required()
def delete_address(address_id):
    user_id = get_jwt_identity()
    address_service.delete_address(address_id, user_id)
    return jsonify(status="success", message="Address deleted successfully."), 200

