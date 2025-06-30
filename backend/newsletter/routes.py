from flask import Blueprint, request, jsonify
from backend.utils.input_sanitizer import InputSanitizer
from backend.services import newsletter_service

newsletter_bp = Blueprint('newsletter_bp', __name__, url_prefix='/api/newsletter')

@newsletter_bp.route('/subscribe', methods=['POST'])
def subscribe_to_newsletter():
    """
    Subscribe an email address to a specific newsletter list (B2C or B2B).
    """
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify(status="error", message="Email is required."), 400

    email = InputSanitizer.sanitize_input(data['email'])
    # Default to 'b2c' if not provided. The frontend for the B2B page should send 'b2b'.
    list_type = InputSanitizer.sanitize_input(data.get('list_type', 'b2c'))

    try:
        # Service handles validation and adding the email to the correct list
        subscriber = newsletter_service.subscribe_email(email, list_type)
        return jsonify(status="success", message="Thank you for subscribing!", data=subscriber.to_dict()), 201
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An error occurred. Please try again later."), 500


@newsletter_bp.route('/unsubscribe/<string:token>', methods=['GET'])
def unsubscribe(token):
    sanitized_token = InputSanitizer.sanitize_input(token)
    if newsletter_service.unsubscribe(sanitized_token):
        return jsonify({'message': 'You have been unsubscribed.'})
    return jsonify({'error': 'Invalid unsubscribe link.'}), 400
