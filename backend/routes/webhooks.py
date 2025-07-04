import stripe
from flask import Blueprint, current_app, jsonify, request

from backend.models.order_models import OrderStatus
from backend.services.order_service import get_order_by_id, update_order_status
from backend.tasks import (
    generate_invoice_for_order_task,
    send_order_confirmation_email_task,
)

webhooks_bp = Blueprint("webhooks", __name__)


@webhooks_bp.route("/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = current_app.config["STRIPE_WEBHOOK_SECRET"]

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        current_app.logger.error(f"Stripe webhook error: {e}")
        return jsonify({"error": str(e)}), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session.get("client_reference_id")

        if order_id:
            order = get_order_by_id(order_id)
            if order and order.status != OrderStatus.COMPLETED:
                update_order_status(order.id, OrderStatus.COMPLETED)

                # Call tasks directly
                send_order_confirmation_email_task.delay(order.id)
                generate_invoice_for_order_task.delay(order.id)
                current_app.logger.info(
                    f"Order {order_id} processing initiated via webhook."
                )
            else:
                current_app.logger.warning(
                    f"Webhook received for already processed or non-existent order {order_id}"
                )

    return jsonify({"status": "success"}), 200
    return {"status": "success"}, 200
