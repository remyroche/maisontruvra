from flask import Blueprint, request, jsonify, current_app
from backend.services.b2b_service import B2BService
from backend.services.quote_service import QuoteService
from backend.utils.decorators import admin_required, login_required
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
@admin_required
def approve_b2b_user(user_id):
    logger = current_app.logger
    b2b_service = B2BService(logger)
    try:
        b2b_service.approve_b2b_account(user_id)
        return jsonify({"message": "B2B account approved."}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.exception(f"Error approving B2B user {user_id}.")
        return jsonify({"error": "An internal error occurred."}), 500

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
@admin_required
def respond_to_quote(quote_id):
    data = request.get_json()
    logger = current_app.logger
    quote_service = QuoteService(logger)
    try:
        quote_service.respond_to_quote(quote_id, data)
        return jsonify({"message": "Quote response sent."}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.exception(f"Error responding to quote {quote_id}.")
        return jsonify({"error": "An internal error occurred."}), 500

@b2b_bp.route('/quotes/<int:quote_id>/accept', methods=['POST'])
@login_required
def accept_quote(quote_id):
    logger = current_app.logger
    quote_service = QuoteService(logger)
    try:
        cart = quote_service.accept_quote_and_create_cart(quote_id, current_user.id)
        return jsonify({"message": "Quote accepted. Cart created.", "cart_id": cart.id}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception(f"Error accepting quote {quote_id} for user {current_user.id}.")
        return jsonify({"error": "An internal error occurred."}), 500
