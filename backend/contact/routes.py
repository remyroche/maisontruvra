from flask import request, jsonify, Blueprint
from ..services.contact_service import ContactService
from ..schemas import ContactFormSchema
from marshmallow import ValidationError
from flask import current_app

# Define the blueprint
contact_bp = Blueprint("contact", __name__, url_prefix="/api/contact")


@contact_bp.route("", methods=["POST"])
def submit_contact_form():
    """
    API endpoint to receive and process contact form submissions.
    It validates the incoming data and uses a service to handle the business logic.
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "No input data provided."}), 400

    # Validate input data against the Marshmallow schema
    try:
        schema = ContactFormSchema()
        data = schema.load(json_data)
    except ValidationError as err:
        # Return validation errors to the client
        return jsonify({"message": "Validation failed.", "errors": err.messages}), 422

    try:
        # Pass the validated data to the service layer
        ContactService.create_contact_message(data)
        return jsonify({"message": "Your message has been received. Thank you!"}), 201
    except Exception as e:
        # Log the exception for debugging purposes
        current_app.logger.error(f"Error processing contact form: {e}")
        return jsonify({"message": "An internal server error occurred."}), 500
