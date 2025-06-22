from flask import Blueprint, request
# Assume 'queue' is an RQ or Celery instance and 'payment_gateway' is the Stripe library

webhooks_bp = Blueprint('webhooks', __name__)

@webhooks_bp.route('/payment-status', methods=['POST'])
def payment_status_webhook():
    """Listens for events from the payment gateway (e.g., Stripe)."""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = payment_gateway.Webhook.construct_event(payload, sig_header, "your_webhook_secret")
        
        order_id = event['data']['object']['metadata'].get('orderId')
        
        if event['type'] == 'checkout.session.completed':
            logger.info({'message': 'Payment success event received', 'orderId': order_id})
            queue.enqueue('worker.finalize_order', order_id)
        elif event['type'] == 'checkout.session.async_payment_failed':
            logger.warning({'message': 'Payment failure event received', 'orderId': order_id})
            queue.enqueue('worker.handle_payment_failure', order_id)

        return 'OK', 200
        
    except ValueError as e: # Invalid payload
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        logger.error({'message': 'Webhook signature verification failed', 'error': str(e)})
        return 'Invalid signature', 400
