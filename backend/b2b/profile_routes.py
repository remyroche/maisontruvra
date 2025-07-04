import logging

from flask import Blueprint, g, jsonify, redirect, render_template, request, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_login import current_user, login_required, logout_user

from backend.extensions import db
from backend.models import Company
from backend.models.address_models import Address
from backend.schemas import (
    AddressSchema,
    B2BProfileSchema,
    B2BProfileUpdateSchema,
    B2BUserInviteSchema,
    B2BUserRemoveSchema,
    B2BUserSchema,
    UserSchema,
)
from backend.services.b2b_service import B2BService
from backend.services.user_service import UserService
from backend.utils.decorators import (
    api_resource_handler,
    b2b_admin_required,
    b2b_required,
)

# --- Blueprint and Service Initialization ---
b2b_profile_bp = Blueprint("b2b_profile_bp", __name__, url_prefix="/api/b2b/profile")
logger = logging.getLogger(__name__)
b2b_service = B2BService(logger)
user_service = UserService(logger)


# --- B2B Profile and User Management ---
@b2b_profile_bp.route("/", methods=["GET"])
@login_required
@b2b_required
@api_resource_handler(response_schema=B2BProfileSchema)
def get_b2b_profile(instance):
    """
    Retrieves the current B2B user's profile.
    """
    return b2b_service.get_b2b_account_by_user_id(instance.id)


@b2b_profile_bp.route("/users", methods=["GET"])
@login_required
@b2b_admin_required
@api_resource_handler(response_schema=B2BUserSchema, is_list=True)
def get_b2b_users(instance):
    """
    Retrieves all users associated with the current B2B admin's company.
    """
    return b2b_service.get_users_for_b2b_account(instance.id)


@b2b_profile_bp.route("/users/invite", methods=["POST"])
@login_required
@b2b_admin_required
@api_resource_handler(
    request_schema=B2BUserInviteSchema, response_schema=B2BUserSchema
)
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
    """
    b2b_service.request_b2b_account_deletion(current_user.id)
    logout_user()  # Log the user out after deletion
    return {
        "message": "Account deletion request processed successfully. You have been logged out."
    }


# --- B2B Address Management ---
@b2b_profile_bp.route("/address", methods=["POST"])
@api_resource_handler(
    model=Address,
    request_schema=AddressSchema,
    response_schema=AddressSchema,
    log_action=True,
)
@b2b_required
@jwt_required()
def add_b2b_address(validated_data):
    """Create a new address for the authenticated B2B user."""
    user_id = get_jwt_identity()
    address = Address(user_id=user_id, **validated_data)
    db.session.add(address)
    return address


@b2b_profile_bp.route("/address/<int:address_id>", methods=["PUT"])
@api_resource_handler(
    model=Address,
    request_schema=AddressSchema,
    response_schema=AddressSchema,
    log_action=True,
)
@b2b_required
@jwt_required()
def update_b2b_address(instance, validated_data):
    """Update an existing address for the authenticated B2B user."""
    for key, value in validated_data.items():
        setattr(instance, key, value)
    return instance


@b2b_profile_bp.route("/address/<int:address_id>", methods=["DELETE"])
@api_resource_handler(model=Address, log_action=True)
@b2b_required
@jwt_required()
def delete_b2b_address(instance):
    """Delete an address for the authenticated B2B user."""
    db.session.delete(instance)
    return None  # Decorator will handle the delete response


# --- Other B2B Routes ---
@b2b_profile_bp.route("/invoices", methods=["GET"])
@b2b_required
@jwt_required()
def get_b2b_invoices():
    user_id = get_jwt_identity()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    try:
        invoices_pagination = b2b_service.get_b2b_invoices_paginated(
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
@login_required
@b2b_required
def company_profile():
    """Affiche le profil de l'entreprise de l'utilisateur B2B."""
    company = current_user.company
    if not company:
        return redirect(url_for("b2b_dashboard_bp.dashboard"))
    return render_template("b2b/company_profile.html", company=company)


@b2b_profile_bp.route("/cart", methods=["GET"])
@b2b_required
@jwt_required()
def get_b2b_cart():
    user_id = get_jwt_identity()
    try:
        cart = b2b_service.get_b2b_cart(user_id)
        return jsonify(cart.to_dict())
    except Exception as e:
        return jsonify(error=str(e)), 500


@b2b_profile_bp.route("/orders/create", methods=["POST"])
@b2b_required
@jwt_required()
def create_b2b_order_from_profile():
    user_id = get_jwt_identity()
    data = request.get_json()
    try:
        order = b2b_service.create_b2b_order(user_id, data)
        return (
            jsonify(order_id=order.id, message="B2B Order created successfully"),
            201,
        )
    except Exception as e:
        return jsonify(error=str(e)), 500
