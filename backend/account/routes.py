from flask import Blueprint, request, jsonify, current_app, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_login import current_user

from backend.database import db
from backend.models.user_models import User
from backend.models.address_models import Address
from backend.services.user_service import UserService
from backend.services.mfa_service import MfaService
from backend.services.address_service import AddressService
from backend.services.email_service import EmailService
from backend.utils.decorators import (
    b2b_user_required,
    admin_required,
    api_resource_handler,
    roles_required,
)
from backend.services.product_service import ProductService  # For product_service
from backend.services.order_service import OrderService  # For order_service
from backend.schemas import (
    AddressSchema,
    LanguageUpdateSchema,
    TwoFactorSetupSchema,
    TwoFactorVerifySchema,
    UserProfileUpdateSchema,
    ChangePasswordSchema,
    UserSchema,
)  # Updated schemas

from backend.services.auth_service import AuthService
from backend.services.exceptions import InvalidCredentialsError, UnauthorizedException

# from backend.schemas import UserProfileUpdateSchema, AddressSchema, ChangePasswordSchema # Duplicate import, removed
from backend.utils.decorators import login_required

account_bp = Blueprint("account_bp", __name__)
user_service = UserService()

mfa_service = MfaService()
address_service = AddressService()
email_service = EmailService()
product_service = ProductService()
order_service = OrderService()


@account_bp.route("/", methods=["GET"])
@api_resource_handler(
    model=User,
    response_schema=UserSchema,
    ownership_exempt_roles=[],  # Only the user themselves can access
    cache_timeout=0,  # No caching for user profiles
    log_action=False,  # No need to log profile views
)
@login_required
def get_account_details():
    """Get current user's account details."""
    # Return the current user
    return current_user


@account_bp.route("/dashboard-data")
@login_required
def get_dashboard_data():
    """
    Provides dashboard data for the logged-in user.
    Differentiates between B2B and B2C users.
    """
    dashboard_service = current_app.service_provider.dashboard
    if hasattr(current_user, "is_b2b") and current_user.is_b2b:
        data = dashboard_service.get_b2b_dashboard_data(current_user.id)
    else:
        data = dashboard_service.get_b2c_dashboard_data(current_user.id)
    return jsonify(data)


@account_bp.route("/b2b-specific-data")
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
        "recent_orders_summary": current_app.service_provider.order.get_recent_orders_summary_for_b2b(
            b2b_account.id
        ),
    }
    return jsonify(data)


@account_bp.route("/admin-only-data")
@admin_required
@roles_required(
    "Admin", "Manager"
)  # This is redundant with admin_required in many cases, but kept for explicit role-based access if needed.
def admin_data():
    """
    Provides summary data intended for an admin user,
    often as a quick overview from a user-centric perspective.
    """
    admin_dashboard_service = current_app.service_provider.admin_dashboard

    # Example data using the admin dashboard service
    data = {
        "pending_b2b_applications": admin_dashboard_service.get_pending_b2b_applications_count(),
        "recent_user_registrations": admin_dashboard_service.get_recent_user_registrations_count(
            days=7
        ),
        "total_active_users": admin_dashboard_service.get_total_active_users_count(),
    }
    return jsonify(data)


@account_bp.route("/api/account/language", methods=["PUT"])
# @api_resource_handler(User, schema=LanguageUpdateSchema(), check_ownership=True) # Old usage
@login_required
@api_resource_handler(
    model=User,
    request_schema=LanguageUpdateSchema,
    response_schema=UserSchema,  # Assuming UserSchema can serialize the user with updated language
    ownership_exempt_roles=[],  # No roles exempt, current user must own
    cache_timeout=0,  # No caching for user-specific updates
    check_ownership=True,  # Explicitly enable ownership check for user endpoint
)
def update_language(user_id):  # The decorator will pass the ID of the resource (User)
    """Updates the language preference for the current user."""
    # user_id comes from the decorator (g.target_object.id or kwargs from route)
    # g.validated_data has 'language'

    # original code: user_id = session.get('user_id') or session.get('b2b_user_id')
    # original code: user_type = session.get('user_type')
    # With login_required and api_resource_handler, g.user.id and g.user object are available
    # and the user_id for the resource (target_object) is passed as an argument.

    user_service.update_user_language(
        user_id, g.validated_data["language"], g.user.user_type
    )

    # Return the updated user object for the decorator to serialize
    return g.target_object


@account_bp.route("/update", methods=["POST"])
@login_required
# This endpoint updates user profile fields (first_name, last_name).
# It's a PUT-like operation on the current user's profile.
@api_resource_handler(
    model=User,
    request_schema=UserProfileUpdateSchema,  # Using UserProfileUpdateSchema for update fields
    response_schema=UserSchema,  # To return the updated user object
    ownership_exempt_roles=[],
    cache_timeout=0,
    check_ownership=True,  # Ensure only current user can update their profile
)
def update_account(user_id):  # Decorator passes the user's ID
    """Update user account details (first name, last name)."""
    # current_user.id is accessible, and user_id is passed by decorator.
    # g.validated_data contains the validated input for profile update.

    updated_user = user_service.update_user(user_id, g.validated_data)
    return updated_user  # Decorator will jsonify with UserSchema


# GET current user's order history
@account_bp.route("/orders", methods=["GET"])
@jwt_required()
@login_required
def get_order_history():
    """
    Get the order history for the currently authenticated user.
    """
    user_id = get_jwt_identity()  # This is the current user's ID
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        # Assumes a service method to get orders for a specific user
        orders_pagination = user_service.get_user_orders_paginated(
            user_id, page=page, per_page=per_page
        )

        return jsonify(
            {
                "status": "success",
                "data": [
                    order.to_dict_for_user() for order in orders_pagination.items
                ],  # Use a user-safe serializer
                "total": orders_pagination.total,
                "pages": orders_pagination.pages,
                "current_page": orders_pagination.page,
            }
        ), 200
    except Exception as e:
        # Log the error e
        current_app.logger.error(
            f"Error fetching order history for user {user_id}: {str(e)}", exc_info=True
        )
        return jsonify(
            status="error", message="An error occurred while fetching order history."
        ), 500


# --- NEW: 2FA Management Routes ---


@account_bp.route("/2fa/setup", methods=["POST"])
@jwt_required()
@login_required
@api_resource_handler(
    model=User,
    request_schema=TwoFactorSetupSchema,  # Empty schema, just for validation hook if needed
    response_schema=None,  # Returns custom data (qr_code, secret)
    ownership_exempt_roles=[],
    cache_timeout=0,
    check_ownership=True,  # Ensure user can only set up 2FA for themselves
)
def setup_2fa(user_id):  # Decorator passes the user's ID
    """Initiates the 2FA setup process for the current user."""
    user = g.target_object  # User object fetched by api_resource_handler

    if user.is_2fa_enabled:  # Use correct attribute name from models/user_models.py
        return jsonify(status="error", message="2FA is already enabled."), 400

    secret = mfa_service.generate_secret()
    user.mfa_secret = secret  # Use correct attribute name
    db.session.commit()  # Commit here to save the secret before generating QR

    uri = mfa_service.get_provisioning_uri(user.email, secret)
    qr_code_uri = mfa_service.generate_qr_code(uri)

    # Decorator won't serialize this, so we return jsonify directly
    return jsonify(
        status="success", data={"qr_code": qr_code_uri, "secret": secret}
    ), 200


@account_bp.route("/profile", methods=["GET"])
@login_required
@api_resource_handler(
    model=User,
    response_schema=UserProfileUpdateSchema,  # Use a schema for serialization for consistency
    ownership_exempt_roles=[],
    cache_timeout=0,  # No caching for user-specific profiles
    check_ownership=True,
)
def get_profile(user_id):
    """Get user profile."""
    # g.target_object is the User object for the current user
    # The decorator will serialize g.target_object using UserProfileUpdateSchema
    return g.target_object


@account_bp.route("/profile", methods=["PUT"])
@api_resource_handler(
    model=User,
    request_schema=UserProfileUpdateSchema,
    response_schema=UserSchema,
    ownership_exempt_roles=[],  # Only the user themselves can update
    cache_timeout=0,  # No caching for user profiles
    log_action=True,  # Log profile updates
)
@login_required
def update_profile():
    """Update user profile."""
    # For profile updates, we work with the current user
    user = current_user

    # Update user with validated data
    for key, value in g.validated_data.items():
        if hasattr(user, key) and key not in [
            "password",
            "id",
        ]:  # Exclude sensitive fields
            setattr(user, key, value)

    return user


@account_bp.route("/change-password", methods=["POST"])
@login_required
@api_resource_handler(
    model=User,  # Target model is User, although no direct ID in route, implicitly current user.
    request_schema=ChangePasswordSchema,
    ownership_exempt_roles=[],
    cache_timeout=0,
    check_ownership=True,  # Implicitly check ownership of current user
)
def change_password(user_id):  # Decorator provides user_id of current user
    """Change user's password."""
    # g.validated_data contains old_password and new_password
    # g.target_object is the User object for the current user
    try:
        AuthService.change_password(
            user_id=user_id,  # Or g.target_object.id
            old_password=g.validated_data["old_password"],
            new_password=g.validated_data["new_password"],
        )
        return jsonify(
            {"message": "Password changed successfully."}
        ), 200  # Custom success message
    except InvalidCredentialsError as e:
        raise e  # Re-raise for api_resource_handler to handle


@account_bp.route("/2fa/verify", methods=["POST"])
# Removed @api_resource_handler from here as it was already applied above
@jwt_required()
@login_required
@api_resource_handler(  # Apply the decorator here
    model=User,
    request_schema=TwoFactorVerifySchema,
    ownership_exempt_roles=[],
    cache_timeout=0,
    check_ownership=True,
)
def verify_2fa(user_id):
    """Verifies the token and enables 2FA for the user."""
    user = g.target_object  # User object fetched by api_resource_handler

    if not user.mfa_secret:  # Use correct attribute name from models/user_models.py
        return jsonify(
            status="error", message="No 2FA setup process was initiated."
        ), 400

    if mfa_service.verify_token(
        user.mfa_secret, g.validated_data["totp_code"]
    ):  # Use correct attribute name
        user.is_2fa_enabled = True  # Use correct attribute name
        db.session.commit()
        return jsonify(status="success", message="2FA enabled successfully."), 200
    else:
        return jsonify(status="error", message="Invalid 2FA token."), 400


@account_bp.route("/2fa/disable", methods=["POST"])
# Removed @api_resource_handler from here as it was already applied above
@jwt_required()
@login_required
@api_resource_handler(  # Apply the decorator here
    model=User,
    request_schema=TwoFactorVerifySchema,
    ownership_exempt_roles=[],
    cache_timeout=0,
    check_ownership=True,
)
def disable_2fa(user_id):
    """Disables 2FA for the user, requires a valid token to do so."""
    user = g.target_object  # User object fetched by api_resource_handler

    if not user.is_2fa_enabled:  # Use correct attribute name from models/user_models.py
        return jsonify(status="error", message="2FA is not currently enabled."), 400

    if mfa_service.verify_token(
        user.mfa_secret, g.validated_data["totp_code"]
    ):  # Use correct attribute name
        user.is_2fa_enabled = False  # Use correct attribute name
        user.mfa_secret = None  # Clear the secret
        db.session.commit()
        email_service.send_security_alert(
            user, "L'authentification à deux facteurs (2FA) a été désactivée"
        )
        return jsonify(status="success", message="2FA disabled successfully."), 200
    else:
        return jsonify(status="error", message="Invalid 2FA token."), 400


@account_bp.route("/addresses", methods=["GET"])
@login_required
def get_addresses():
    # This is a list endpoint, api_resource_handler is not ideal for this
    address_service = AddressService()
    addresses = address_service.get_user_addresses(current_user.id)
    return jsonify([address.to_dict() for address in addresses])


@account_bp.route("/addresses", methods=["POST"])
@api_resource_handler(
    model=Address,
    request_schema=AddressSchema,
    response_schema=AddressSchema,
    ownership_exempt_roles=[],  # Only the user themselves can create
    cache_timeout=0,  # No caching for addresses
    log_action=True,  # Log address creation
)
@login_required
def add_address():
    """Add a new address for the user."""
    # Create new address with validated data
    address = Address()
    address.user_id = current_user.id
    for key, value in g.validated_data.items():
        if hasattr(address, key):
            setattr(address, key, value)

    db.session.add(address)
    return address


@account_bp.route("/addresses/<int:address_id>", methods=["PUT"])
@api_resource_handler(
    model=Address,
    request_schema=AddressSchema,
    response_schema=AddressSchema,
    ownership_exempt_roles=[],  # Only the owner can update
    cache_timeout=0,  # No caching for addresses
    log_action=True,  # Log address updates
)
@login_required
def update_address(address_id):
    """Update an existing address."""
    # Address is already fetched and validated by decorator
    address = g.target_object

    # Verify ownership
    if address.user_id != current_user.id:
        raise UnauthorizedException("You do not have permission to update this address")

    # Update address with validated data
    for key, value in g.validated_data.items():
        if hasattr(address, key):
            setattr(address, key, value)

    return address


@account_bp.route("/addresses/<int:address_id>", methods=["DELETE"])
@login_required
@api_resource_handler(
    model=Address,
    ownership_exempt_roles=[],
    cache_timeout=0,
    check_ownership=True,  # Crucial for addresses
)
def delete_address(address_id):
    """Delete an address."""
    # user_id is implicit from login_required and check_ownership
    address_service.delete_address(address_id=address_id, user_id=current_user.id)
    return None  # Return None for successful deletion, decorator will send message
