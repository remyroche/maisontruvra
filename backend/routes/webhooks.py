from flask import Blueprint, request, jsonify
from backend.services.webhook_service import WebhookService # Assumed service
import os

webhooks_bp = Blueprint('webhooks_bp', __name__, url_prefix='/webhooks')

@webhooks_bp.route('/stripe', methods=['POST'])
def stripe_webhook():
    """
    Handle incoming webhooks from Stripe.
    This endpoint must be secured by verifying the Stripe signature.
    """
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.environ.get('STRIPE_ENDPOINT_SECRET')

    if not sig_header:
        return jsonify(status="error", message="Missing Stripe-Signature header"), 400
    if not endpoint_secret:
        # Proper logging should be implemented here to alert administrators.
        return jsonify(status="error", message="Stripe endpoint secret is not configured."), 500

    try:
        # The service should handle the verification and processing of the event
        event = WebhookService.process_stripe_event(payload, sig_header, endpoint_secret)
        
        if event:
            return jsonify(status="success", message=f"Processed event: {event.type}"), 200
        else:
            return jsonify(status="error", message="Could not process event."), 400

    except ValueError as e: # Invalid payload
        return jsonify(status="error", message=str(e)), 400
    except Exception as e: # Invalid signature or other processing error
        # Log error e
        return jsonify(status="error", message=str(e)), 400

