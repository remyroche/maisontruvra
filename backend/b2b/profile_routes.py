from flask import (
    Blueprint,
    request,
    jsonify,
    g,
    redirect,
    url_for,
    flash,
    render_template,
)
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.b2b_service import B2BService
from backend.utils.decorators import (
    b2b_user_required,
    b2b_admin_required,
    api_resource_handler,
)
from backend.models.address_models import Address
from backend.schemas import UserSchema, AddressSchema
from backend.extensions import db
from flask_login import current_user
from backend.models import db, Company
from backend.utils.decorators import login_required

b2b_profile_bp = Blueprint("b2b_profile_bp", __name__, url_prefix="/api/b2b/profile")
b2b_service = B2BService()
user_service = UserService()


@b2b_profile_bp.route("/", methods=["GET"])
@login_required
@b2b_required
@api_resource_handler(response_schema=B2BProfileSchema)
def get_b2b_profile():
    """
    Retrieves the current B2B user's profile.
    """
    return b2b_service.get_b2b_account_by_user_id(current_user.id)


# --- B2B User Management ---


@b2b_profile_bp.route("/users", methods=["GET"])
@login_required
@b2b_admin_required
@api_resource_handler(response_schema=B2BUserSchema, is_list=True)
def get_b2b_users():
    """
    Retrieves all users associated with the current B2B admin's company.
    """
    return b2b_service.get_users_for_b2b_account(current_user.id)


@b2b_profile_bp.route("/users/invite", methods=["POST"])
@login_required
@b2b_admin_required
@api_resource_handler(request_schema=B2BUserInviteSchema, response_schema=B2BUserSchema)
def invite_b2b_user(validated_data):
    """
    Invites a new user to the B2B account.
    """
    invited_user = b2b_service.invite_b2b_user(current_user.id, validated_data)
    return invited_user


@b2b_profile_bp.route("/users/remove", methods=["POST"])
@login_required
@b2b_admin_required
@api_resource_handler(request_schema=B2BUserRemoveSchema)
def remove_b2b_user(validated_data):
    """
    Removes a user from the B2B account.
    """
    b2b_service.remove_b2b_user(current_user.id, validated_data)
    return {"message": "User removed successfully from the B2B account."}


@b2b_profile_bp.route("/", methods=["PUT"])
@login_required
@b2b_required
@api_resource_handler(
    request_schema=B2BProfileUpdateSchema, response_schema=B2BProfileSchema
)
def update_b2b_profile(validated_data):
    """
    Updates the current B2B user's profile.
    The decorator handles validation, serialization, and error handling.
    """
    b2b_account = b2b_service.update_b2b_account(current_user.id, validated_data)
    return b2b_account


@b2b_profile_bp.route("/delete", methods=["DELETE"])
@login_required
@b2b_required
@api_resource_handler()
def delete_b2b_account():
    """
    Endpoint for a B2B user to request soft-deletion of their own account.
    The decorator handles response formatting and error catching.
    """
    b2b_service.request_b2b_account_deletion(current_user.id)
    logout_user()  # Log the user out after deletion
    return {
        "message": "Account deletion request processed successfully. You have been logged out."
    }


@b2b_profile_bp.route("/address", methods=["POST"])
@api_resource_handler(
    model=Address,
    request_schema=AddressSchema,
    response_schema=AddressSchema,
    ownership_exempt_roles=[],  # Only the user themselves can create
    cache_timeout=0,  # No caching for addresses
    log_action=True,
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


@b2b_profile_bp.route("/address/<int:address_id>", methods=["PUT"])
@api_resource_handler(
    model=Address,
    request_schema=AddressSchema,
    response_schema=AddressSchema,
    ownership_exempt_roles=[],  # Only the owner can update
    cache_timeout=0,  # No caching for addresses
    log_action=True,
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


@b2b_profile_bp.route("/address/<int:address_id>", methods=["DELETE"])
@api_resource_handler(
    model=Address,
    ownership_exempt_roles=[],  # Only the owner can delete
    cache_timeout=0,  # No caching for addresses
    log_action=True,
)
@b2b_user_required
@jwt_required()
def delete_b2b_address(address_id):
    """Delete an address for the authenticated B2B user."""
    # Address is already fetched and validated by decorator
    address = g.target_object
    db.session.delete(address)
    return None  # Decorator will handle the delete response


@b2b_profile_bp.route("/invoices", methods=["GET"])
@b2b_user_required
def get_b2b_invoices():
    user_id = get_jwt_identity()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    try:
        invoices_pagination = B2BService.get_b2b_invoices_paginated(
            user_id, page, per_page
        )
        return jsonify(
            {
                "items": [invoice.to_dict() for invoice in invoices_pagination.items],
                "total": invoices_pagination.total,
                "pages": invoices_pagination.pages,
                "current_page": invoices_pagination.page,
            }
        )
    except Exception as e:
        return jsonify(error=str(e)), 500


@b2b_profile_bp.route("/company/profile")
@api_resource_handler(
    model=Company,
    response_schema=UserSchema,
    ownership_exempt_roles=[],  # Only the user themselves can access
    cache_timeout=0,  # No caching for company profiles
    log_action=True,
)
@b2b_user_required
def company_profile():
    """Affiche le profil de l'entreprise de l'utilisateur B2B."""
    # La logique est correcte car elle utilise `current_user.company`
    company = current_user.company
    if not company:
        flash("Profil d'entreprise non trouvé.", "warning")
        return redirect(url_for("b2b_dashboard_bp.dashboard"))
    return render_template("b2b/company_profile.html", company=company)


@b2b_profile_bp.route("/cart", methods=["GET"])
@b2b_user_required
def get_b2b_cart():
    user_id = get_jwt_identity()
    try:
        cart = B2BService.get_b2b_cart(user_id)
        return jsonify(cart.to_dict())
    except Exception as e:
        return jsonify(error=str(e)), 500


@b2b_profile_bp.route("/orders/create", methods=["POST"])
@b2b_user_required
def create_b2b_order():
    user_id = get_jwt_identity()
    data = request.get_json()
    try:
        order = B2BService.create_b2b_order(user_id, data)
        return jsonify(order_id=order.id, message="B2B Order created successfully"), 201
    except Exception as e:
        return jsonify(error=str(e)), 500
