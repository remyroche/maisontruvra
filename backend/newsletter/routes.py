from flask import Blueprint, request, jsonify
from backend.services.newsletter_service import NewsletterService
from backend.utils.sanitization import sanitize_input

newsletter_bp = Blueprint('newsletter_bp', __name__, url_prefix='/api/newsletter')

@newsletter_bp.route('/subscribe', methods=['POST'])
def subscribe_to_newsletter():
    """
    Subscribe an email address to a specific newsletter list (B2C or B2B).
    """
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify(status="error", message="Email is required."), 400

    email = sanitize_input(data['email'])
    # Default to 'b2c' if not provided. The frontend for the B2B page should send 'b2b'.
    list_type = sanitize_input(data.get('list_type', 'b2c'))

    try:
        # Service handles validation and adding the email to the correct list
        subscriber = NewsletterService.subscribe_email(email, list_type)
        return jsonify(status="success", message="Thank you for subscribing!", data=subscriber.to_dict()), 201
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An error occurred. Please try again later."), 500
