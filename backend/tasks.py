import logging
from flask import current_app
from backend.celery_worker import celery

# Import all necessary services
from backend.services.email_service import EmailService
from backend.services.loyalty_service import LoyaltyService
from backend.services.invoice_service import InvoiceService
from backend.services.passport_service import PassportService
from backend.services.order_service import OrderService # Import the new service

logger = logging.getLogger(__name__)

# --- Task Decorator Definitions ---
# A standard decorator for resilient, one-off tasks (e.g., triggered by user action)
resilient_task = celery.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 5}, # Added countdown for clarity
    retry_backoff=True,
    soft_time_limit=300,  # 5 minutes
    time_limit=600        # 10 minutes
)

# A standard decorator for scheduled (beat) tasks
scheduled_task = celery.task(
    bind=True,
    soft_time_limit=1800, # 30 minutes
    time_limit=3600       # 1 hour
)


# --- Task Definitions ---

@resilient_task
def send_email_task(self, recipient, subject, template_name, context):
    """Celery task to send an email asynchronously by calling the EmailService."""
    logger.info(f"Executing task id {self.request.id} to send email to {recipient}")
    EmailService.send_email_immediately(recipient, subject, template_name, context)


@resilient_task
def generate_invoice_pdf_task(self, order_id):
    """Celery task to generate a PDF invoice by calling the InvoiceService."""
    logger.info(f"Executing invoice generation task id {self.request.id} for order {order_id}")
    InvoiceService.generate_pdf(order_id)
    logger.info(f"Successfully generated invoice for order {order_id}")


@resilient_task
def generate_passport_pdf_task(self, passport_id):
    """Celery task to generate a product passport PDF by calling the PassportService."""
    logger.info(f"Executing passport generation task id {self.request.id} for passport {passport_id}")
    PassportService.generate_pdf(passport_id)
    logger.info(f"Successfully generated passport for {passport_id}")


@resilient_task
def finalize_order_task(self, order_id):
    """
    Orchestration task to finalize an order after payment.
    It calls other tasks for invoice generation and confirmation emails.
    """
    logger.info(f"Executing 'finalize_order_task' for order {order_id}")
    # In a real scenario, you might have a service method to update order status
    # OrderService.set_status_to_processing(order_id)
    
    # Queue subsequent, independent jobs.
    generate_invoice_pdf_task.delay(order_id)
    
    # You would fetch the user's email and details to send the confirmation.
    # For now, this is a placeholder for the email context.
    # user = OrderService.get_user_for_order(order_id)
    email_context = {'order_id': order_id, 'customer_name': 'Valued Customer'}
    send_email_task.delay(
        recipient='user@example.com', # Replace with user.email
        subject=f"Your Order Confirmation #{order_id}",
        template_name='emails/order_confirmation.html',
        context=email_context
    )


@resilient_task
def fulfill_order_task(self, order_id):
    """
    Celery task to trigger the order fulfillment process by calling the OrderService.
    """
    logger.info(f"Executing fulfillment task for order {order_id}")
    OrderService.fulfill_order(order_id)


# --- Scheduled Tasks ---

@scheduled_task
def expire_loyalty_points_task(self):
    """Scheduled task to expire old loyalty points via LoyaltyService."""
    logger.info("Starting scheduled task: expire_loyalty_points_task")
    count = LoyaltyService.expire_points_task()
    logger.info(f"Finished scheduled task: Expired {count} loyalty point transactions.")
    return f"Expired {count} loyalty point records."


@scheduled_task
def update_all_b2b_loyalty_tiers(self):
    """Scheduled task to recalculate all B2B user loyalty tiers via LoyaltyService."""
    logger.info("Starting scheduled task: update_all_b2b_loyalty_tiers")
    count = LoyaltyService.update_user_tiers_task()
    logger.info(f"Finished scheduled task: Updated loyalty tiers for {count} active B2B users.")
    return f"Updated {count} B2B loyalty tiers."

