from backend import create_app, celery

app = create_app()
app.app_context().push()


def finalize_order(order_id):
    """Finalizes an order after successful payment."""
    logger.info(f"Processing 'finalize_order' job for order {order_id}")
    try:
        # 1. Update order status to 'Processing'.
        # 2. Decrement inventory for each item in the order.
        # 3. Award points to the user.
        # All within a single database transaction.

        # Queue subsequent jobs
        queue.enqueue('worker.send_email', {'type': 'orderConfirmation', 'orderId': order_id})
        queue.enqueue('worker.generate_invoice', order_id)
    except Exception as e:
        logger.error({'message': f"Job 'finalize_order' failed for order {order_id}", 'error': str(e)})
        raise # Re-raise to allow for retries

def send_email(email_details):
    """Sends an email via a third-party service."""
    recipient = email_details.get('recipient')
    logger.info(f"Sending email to {recipient}")
    try:
        # Integrate with an email service like SendGrid, Mailgun, etc.
        email_service.send(email_details)
    except Exception as e:
        logger.error({'message': f"Job 'send_email' failed for recipient {recipient}", 'error': str(e)})
        raise
