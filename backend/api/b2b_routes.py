import logging

from flask import Blueprint, g, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_login import current_user

from backend.models.b2b_models import B2BAccountRequest
from backend.models.quote_models import Quote
from backend.models.user_models import User
from backend.schemas import (
    B2BAccountRequestSchema,
    QuoteResponseSchema,
    QuoteSchema,
    UserSchema,
)
from backend.services.b2b_service import B2BService
from backend.services.exceptions import AuthorizationException, ValidationException
from backend.services.quote_service import QuoteService
from backend.utils.decorators import (
    admin_required,
    api_resource_handler,
    login_required,
)

# --- Blueprint and Service Initialization ---
b2b_bp = Blueprint("b2b_api", __name__, url_prefix="/api/b2b")
logger = logging.getLogger(__name__)
b2b_service = B2BService(logger)
quote_service = QuoteService(logger)


# --- B2B Registration and Application Routes ---
@b2b_bp.route("/register", methods=["POST"])
@api_resource_handler(
    model=B2BAccountRequest,
    request_schema=B2BAccountRequestSchema,
    response_schema=B2BAccountRequestSchema,
    log_action=True,
)
def register_b2b_account():
    """
    Endpoint for B2B account registration requests.
    The decorator handles validation and response formatting.
    """
    b2b_request = b2b_service.request_b2b_account(g.validated_data)
    response = jsonify(B2BAccountRequestSchema().dump(b2b_request))
    response.status_code = 202  # Use 202 Accepted as the request is pending approval
    return response


@b2b_bp.route("/applications", methods=["GET"])
@admin_required
def get_b2b_applications():
    """
    Admin endpoint to view pending B2B applications.
    """
    users = b2b_service.get_all_b2b_users(status="pending")
    # Use a schema to serialize user data properly
    return (
        jsonify(
            [
                {"id": u.id, "email": u.email, "company_name": u.company_name}
                for u in users
            ]
        ),
        200,
    )


@b2b_bp.route("/approve/<int:user_id>", methods=["POST"])
@api_resource_handler(
    model=User,
    response_schema=UserSchema,
    ownership_exempt_roles=["Admin", "Manager"],
    cache_timeout=0,
    log_action=True,
)
@admin_required
def approve_b2b_user(user_id):
    """
    Admin approves a B2B user account.
    """
    user = g.target_object
    try:
        approved_user = b2b_service.approve_b2b_account(user_id)
        return approved_user or user
    except ValueError as e:
        raise ValidationException(str(e)) from e


# --- B2B Quote Routes ---
@b2b_bp.route("/quotes/request", methods=["POST"])
@jwt_required()
@api_resource_handler(
    model=Quote,
    request_schema=QuoteSchema,
    response_schema=QuoteSchema,
    log_action=True,
)
def request_quote():
    """
    Authenticated B2B user requests a new quote.
    """
    user_id = get_jwt_identity()
    new_quote = b2b_service.create_quote_request(user_id, g.validated_data)
    return new_quote


@b2b_bp.route("/quotes/<int:quote_id>/respond", methods=["POST"])
@api_resource_handler(
    model=Quote,
    request_schema=QuoteResponseSchema,
    response_schema=QuoteSchema,
    ownership_exempt_roles=["Admin", "Manager"],
    eager_loads=["items", "user"],
    cache_timeout=0,
    log_action=True,
)
@admin_required
def respond_to_quote(quote_id):
    """
    Admin responds to a quote request with pricing.
    """
    try:
        updated_quote = quote_service.respond_to_quote(quote_id, g.validated_data)
        return updated_quote
    except ValueError as e:
        raise ValidationException(str(e)) from e


@b2b_bp.route("/quotes/<int:quote_id>/accept", methods=["POST"])
@api_resource_handler(
    model=Quote,
    response_schema=QuoteSchema,
    ownership_exempt_roles=[],  # Only the quote owner can accept
    eager_loads=["items", "user"],
    cache_timeout=0,
    log_action=True,
)
@login_required
def accept_quote(quote_id):
    """
    User accepts a quote and creates a cart from it.
    """
    quote = g.target_object

    # Verify ownership
    if quote.user_id != current_user.id:
        raise AuthorizationException("You do not have permission to accept this quote")

    try:
        cart = quote_service.accept_quote_and_create_cart(quote_id, current_user.id)
        return (
            jsonify({"message": "Quote accepted. Cart created.", "cart_id": cart.id}),
            200,
        )
    except ValueError as e:
        raise ValidationException(str(e)) from e
