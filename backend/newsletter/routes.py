from flask import Blueprint, request, jsonify
from backend.services.newsletter_service import NewsletterService
from backend.services.exceptions import ServiceException
from flask import Blueprint, request, jsonify
from backend.services.newsletter_service import NewsletterService
from backend.utils.sanitization import sanitize_input

newsletter_bp = Blueprint('newsletter_bp', __name__, url_prefix='/api/newsletter')

# Subscribe to the newsletter
@newsletter_bp.route('/subscribe', methods=['POST'])
def subscribe_to_newsletter():
    """
    Subscribe an email address to the newsletter list.
    """
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify(status="error", message="Email is required."), 400

    email = sanitize_input(data['email'])

    try:
        # The service handles validation and adding the email.
        # It should also handle cases where the email is already subscribed.
        subscriber = NewsletterService.subscribe_email(email)
        return jsonify(status="success", message="Thank you for subscribing!", data=subscriber.to_dict()), 201
    except ValueError as e: # Handles invalid email or existing subscription
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An error occurred. Please try again later."), 500

