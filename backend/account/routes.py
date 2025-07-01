from flask import Blueprint, request, jsonify, session, current_app, g
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from marshmallow import ValidationError

from backend.database import db
from backend.models.user_models import User
from backend.models.address_models import Address
from backend.services.user_service import UserService
from backend.services.mfa_service import MfaService
from backend.services.address_service import AddressService
from backend.services.email_service import EmailService
from backend.utils.input_sanitizer import InputSanitizer
from backend.utils.auth_helpers import send_password_change_email
from backend.utils.decorators import b2b_user_required, admin_required, api_resource_handler, roles_required
from backend.services.product_service import ProductService # For product_service
from backend.services.order_service import OrderService # For order_service
from backend.admin_api.user_management_routes import admin_user_management_bp
from backend.products.routes import products_bp
from backend.orders.routes import orders_bp
from backend.services.user_service import UserService
from backend.services.dashboard_service import DashboardService
from backend.schemas import UpdateUserSchema, UpdatePasswordSchema, AddressSchema, LanguageUpdateSchema, TwoFactorSetupSchema, TwoFactorVerifySchema
from backend.models.address_models import Address

from backend.services.auth_service import AuthService
from backend.services.exceptions import InvalidCredentialsError
from backend.schemas import UserProfileUpdateSchema, AddressSchema, ChangePasswordSchema
from backend.utils.decorators import login_required_json




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

@account_bp.route('/dashboard-data')
@login_required
def get_dashboard_data():
    """
    Provides dashboard data for the logged-in user.
    Differentiates between B2B and B2C users.
    """
    dashboard_service = current_app.service_provider.dashboard
    if hasattr(current_user, 'is_b2b') and current_user.is_b2b:
        data = dashboard_service.get_b2b_dashboard_data(current_user.id)
    else:
        data = dashboard_service.get_b2c_dashboard_data(current_user.id)
    return jsonify(data)

@account_bp.route('/b2b-specific-data')
@b2b_user_required
def b2b_data():
    """
    Provides specific, detailed data for a B2B user.
    This could include company details, team members, and contract information.
    """
    b2b_service = current_app.service_provider.b2b
    
    # The b2b_user_required decorator ensures current_user.b2b_user is not None
    b2b_account = b2b_service.get_b2b_account_details(current_user.b2b_user.id)
    
    if not b2b_account:
        return jsonify({"error": "B2B account not found"}), 404
        
    # Example data structure
    data = {
        "company_name": b2b_account.company_name,
        "vat_number": b2b_account.vat_number,
        "status": b2b_account.status.value,
        "users_count": b2b_service.get_b2b_user_count(b2b_account.id),
        "recent_orders_summary": current_app.service_provider.order.get_recent_orders_summary_for_b2b(b2b_account.id)
    }
    return jsonify(data)

@account_bp.route('/admin-only-data')
@admin_required
@roles_required ('Admin', 'Manager')
def admin_data():
    """
    Provides summary data intended for an admin user,
    often as a quick overview from a user-centric perspective.
    """
    admin_dashboard_service = current_app.service_provider.admin_dashboard
    
    # Example data using the admin dashboard service
    data = {
        "pending_b2b_applications": admin_dashboard_service.get_pending_b2b_applications_count(),
        "recent_user_registrations": admin_dashboard_service.get_recent_user_registrations_count(days=7),
        "total_active_users": admin_dashboard_service.get_total_active_users_count()
    }
    return jsonify(data)


@account_bp.route('/api/account/language', methods=['PUT'])
@api_resource_handler(User, schema=LanguageUpdateSchema(), check_ownership=True)
@login_required
def update_language():
    user_id = session.get('user_id') or session.get('b2b_user_id')
    user_type = session.get('user_type')

    try:
        user_service.update_user_language(user_id, g.validated_data['language'], user_type)
        return jsonify({"message": "Language updated successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@account_bp.route('/update', methods=['POST'])
@login_required
def update_account(): 
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Invalid JSON data provided"}), 400
    
    # Validate input using marshmallow schema
    try:
        schema = UpdateUserSchema()
        validated_data = schema.load(json_data)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "errors": err.messages}), 400
    
    updated_user = user_service.update_user(current_user.id, validated_data)
    return jsonify(updated_user.to_user_dict())


# --- Misplaced Admin Route (should be in admin_api/user_management_routes.py) ---
@admin_user_management_bp.route('/<int:user_id>', methods=['GET'])
@roles_required ('Admin', 'Manager')
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





# GET current user's order history
@account_bp.route('/orders', methods=['GET'])
@jwt_required()
@login_required
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
@login_required
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


@account_bp.route('/profile', methods=['GET'])
@login_required_json
def get_profile():
    user_service = UserService()
    profile_data = user_service.get_user_profile(current_user.id)
    return jsonify(profile_data)

@account_bp.route('/profile', methods=['PUT'])
@login_required_json
def update_profile():
    """ Update user profile. """
    schema = UserProfileUpdateSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user_service = UserService()
    try:
        updated_user = user_service.update_profile(current_user.id, data)
        return jsonify({"message": "Profile updated successfully.", "user": updated_user.to_dict()})
    except ValueError as e:
        return jsonify({"error": str(e)}), 409 # Conflict, e.g. email exists
    except Exception as e:
        return jsonify({"error": "Failed to update profile."}), 500

@account_bp.route('/change-password', methods=['POST'])
@login_required_json
def change_password():
    """ Change user's password. """
    schema = ChangePasswordSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    auth_service = AuthService()
    try:
        auth_service.change_password(
            user_id=current_user.id,
            old_password=data['old_password'],
            new_password=data['new_password']
        )
        return jsonify({"message": "Password changed successfully."}), 200
    except InvalidCredentialsError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": "An error occurred while changing password."}), 500

@account_bp.route('/2fa/verify', methods=['POST'])
@api_resource_handler(User, schema=TwoFactorVerifySchema(), check_ownership=True)
@jwt_required()
@login_required
def verify_2fa():
    """Verifies the token and enables 2FA for the user."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user.two_factor_secret: # Use correct attribute name
        return jsonify(status="error", message="No 2FA setup process was initiated."), 400
        
    if mfa_service.verify_token(user.two_factor_secret, g.validated_data['totp_code']): # Use correct attribute name
        user.two_factor_enabled = True # Use correct attribute name
        db.session.commit()
        return jsonify(status="success", message="2FA enabled successfully."), 200
    else:
        return jsonify(status="error", message="Invalid 2FA token."), 400


@account_bp.route('/2fa/disable', methods=['POST'])
@api_resource_handler(User, schema=TwoFactorVerifySchema(), check_ownership=True)
@jwt_required()
@login_required
def disable_2fa():
    """Disables 2FA for the user, requires a valid token to do so."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user.two_factor_enabled: # Use correct attribute name
        return jsonify(status="error", message="2FA is not currently enabled."), 400

    if mfa_service.verify_token(user.two_factor_secret, g.validated_data['totp_code']): # Use correct attribute name
        user.two_factor_enabled = False # Use correct attribute name
        user.two_factor_secret = None # Clear the secret
        db.session.commit()
        email_service.send_security_alert(user, "L'authentification à deux facteurs (2FA) a été désactivée")
        return jsonify(status="success", message="2FA disabled successfully."), 200
    else:
        return jsonify(status="error", message="Invalid 2FA token."), 400


@account_bp.route('/addresses', methods=['GET'])
@login_required_json
def get_addresses():
    address_service = AddressService()
    addresses = address_service.get_user_addresses(current_user.id)
    return jsonify([address.to_dict() for address in addresses])

@account_bp.route('/addresses', methods=['POST'])
@login_required_json
def add_address():
    """ Add a new address for the user. """
    schema = AddressSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    address_service = AddressService()
    try:
        address = address_service.create_address(user_id=current_user.id, data=data)
        return jsonify({"message": "Address added successfully.", "address": address.to_dict()}), 201
    except Exception as e:
        return jsonify({"error": "Failed to add address."}), 500

@account_bp.route('/addresses/<int:address_id>', methods=['PUT'])
@login_required_json
def update_address(address_id):
    """ Update an existing address. """
    schema = AddressSchema()
    try:
        data = schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400

    address_service = AddressService()
    try:
        address = address_service.update_address(address_id=address_id, user_id=current_user.id, data=data)
        if not address:
            return jsonify({"error": "Address not found or you don't have permission to edit it."}), 404
        return jsonify({"message": "Address updated successfully.", "address": address.to_dict()})
    except Exception as e:
        return jsonify({"error": "Failed to update address."}), 500

@account_bp.route('/addresses/<int:address_id>', methods=['DELETE'])
@login_required_json
def delete_address(address_id):
    address_service = AddressService()
    try:
        success = address_service.delete_address(address_id=address_id, user_id=current_user.id)
        if not success:
            return jsonify({"error": "Address not found or you don't have permission to delete it."}), 404
        return jsonify({"message": "Address deleted successfully."})
    except Exception as e:
        return jsonify({"error": "Failed to delete address."}), 500
