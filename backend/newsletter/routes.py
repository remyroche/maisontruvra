from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from backend.utils.input_sanitizer import InputSanitizer
from backend.services import newsletter_service
from backend.schemas import NewsletterSubscriptionSchema

newsletter_bp = Blueprint("newsletter_bp", __name__, url_prefix="/api/newsletter")


@newsletter_bp.route("/subscribe", methods=["POST"])
def subscribe_to_newsletter():
    """
    Subscribe an email address to a specific newsletter list (B2C or B2B).
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify(status="error", message="Invalid JSON data provided."), 400

    # Validate input using marshmallow schema
    try:
        schema = NewsletterSubscriptionSchema()
        validated_data = schema.load(json_data)
    except ValidationError as err:
        return jsonify(
            status="error", message="Validation failed.", errors=err.messages
        ), 400

    try:
        # Service handles validation and adding the email to the correct list
        subscriber = newsletter_service.subscribe_email(
            validated_data["email"], validated_data["list_type"]
        )
        return jsonify(
            status="success",
            message="Thank you for subscribing!",
            data=subscriber.to_dict(),
        ), 201
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception:
        # Log error e
        return jsonify(
            status="error", message="An error occurred. Please try again later."
        ), 500


@newsletter_bp.route("/unsubscribe/<string:token>", methods=["GET"])
def unsubscribe(token):
    sanitized_token = InputSanitizer.sanitize_input(token)
    if newsletter_service.unsubscribe(sanitized_token):
        return jsonify({"message": "You have been unsubscribed."})
    return jsonify({"error": "Invalid unsubscribe link."}), 400
