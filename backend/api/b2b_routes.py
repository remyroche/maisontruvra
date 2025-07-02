from flask import Blueprint, request, jsonify, current_app, g
from backend.services.b2b_service import B2BService
from backend.services.quote_service import QuoteService
from backend.utils.decorators import admin_required, login_required, api_resource_handler
from backend.models.quote_models import Quote
from backend.models.user_models import User
from backend.schemas import QuoteSchema, QuoteResponseSchema, UserSchema
from backend.services.exceptions import NotFoundException, ValidationException, AuthorizationException
from flask_login import current_user

b2b_bp = Blueprint('b2b_api', __name__, url_prefix='/api/b2b')

@b2b_bp.route('/apply', methods=['POST'])
def apply_for_b2b():
    data = request.get_json()
    logger = current_app.logger
    b2b_service = B2BService(logger)
    try:
        user = b2b_service.apply_for_b2b_account(data)
        return jsonify({"message": "B2B application submitted successfully.", "user_id": user.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception("Error during B2B application.")
        return jsonify({"error": "An internal error occurred."}), 500

@b2b_bp.route('/applications', methods=['GET'])
@admin_required
def get_b2b_applications():
    logger = current_app.logger
    b2b_service = B2BService(logger)
    users = b2b_service.get_all_b2b_users(status='pending')
    # Use a schema to serialize user data properly
    return jsonify([{"id": u.id, "email": u.email, "company_name": u.company_name} for u in users]), 200

@b2b_bp.route('/approve/<int:user_id>', methods=['POST'])
@api_resource_handler(
    model=User,
    response_schema=UserSchema,
    ownership_exempt_roles=['Admin', 'Manager'],  # Staff can approve any user
    cache_timeout=0,  # No caching for user approval
    log_action=True  # Log user approvals
)
@admin_required
def approve_b2b_user(user_id):
    """
    Admin approves a B2B user account.
    """
    # User is already fetched and validated by decorator
    user = g.target_object
    
    logger = current_app.logger
    b2b_service = B2BService(logger)
    
    try:
        approved_user = b2b_service.approve_b2b_account(user_id)
        return approved_user or user
    except ValueError as e:
        raise ValidationException(str(e))

@b2b_bp.route('/quotes/request', methods=['POST'])
@login_required
def request_quote():
    data = request.get_json()
    logger = current_app.logger
    quote_service = QuoteService(logger)
    try:
        quote = quote_service.create_quote_request(current_user.id, data['items'])
        return jsonify({"message": "Quote request created.", "quote_id": quote.id}), 201
    except Exception as e:
        logger.exception(f"Error creating quote for user {current_user.id}.")
        return jsonify({"error": "An internal error occurred."}), 500

@b2b_bp.route('/quotes/<int:quote_id>/respond', methods=['POST'])
@api_resource_handler(
    model=Quote,
    request_schema=QuoteResponseSchema,
    response_schema=QuoteSchema,
    ownership_exempt_roles=['Admin', 'Manager'],  # Staff can respond to any quote
    eager_loads=['items', 'user'],  # Load quote details
    cache_timeout=0,  # No caching for quote responses
    log_action=True  # Log quote responses
)
@admin_required
def respond_to_quote(quote_id):
    """
    Admin responds to a quote request with pricing.
    """
    # Quote is already fetched and validated by decorator
    quote = g.target_object
    
    # Update quote with response data
    logger = current_app.logger
    quote_service = QuoteService(logger)
    
    try:
        updated_quote = quote_service.respond_to_quote(quote_id, g.validated_data)
        return updated_quote
    except ValueError as e:
        raise ValidationException(str(e))

@b2b_bp.route('/quotes/<int:quote_id>/accept', methods=['POST'])
@api_resource_handler(
    model=Quote,
    response_schema=QuoteSchema,
    ownership_exempt_roles=[],  # Only the quote owner can accept
    eager_loads=['items', 'user'],  # Load quote details
    cache_timeout=0,  # No caching for quote acceptance
    log_action=True  # Log quote acceptance
)
@login_required
def accept_quote(quote_id):
    """
    User accepts a quote and creates a cart from it.
    """
    # Quote is already fetched and validated by decorator
    quote = g.target_object
    
    # Verify ownership
    if quote.user_id != current_user.id:
        raise AuthorizationException("You do not have permission to accept this quote")
    
    # Accept quote and create cart
    logger = current_app.logger
    quote_service = QuoteService(logger)
    
    try:
        cart = quote_service.accept_quote_and_create_cart(quote_id, current_user.id)
        return jsonify({"message": "Quote accepted. Cart created.", "cart_id": cart.id}), 200
    except ValueError as e:
        raise ValidationException(str(e))
