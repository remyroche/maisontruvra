import logging
from flask import current_app
from backend.celery_worker import celery
from backend.extensions import cache, db

# Import all necessary services and models
from backend.services.email_service import EmailService
from backend.services.loyalty_service import LoyaltyService
from backend.services.invoice_service import InvoiceService
from backend.services.passport_service import PassportService
from backend.services.order_service import OrderService
from backend.models import B2BUser, User, Order

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
    with current_app.app_context():
        EmailService.send_email_immediately(recipient, subject, template_name, context)


@resilient_task
def generate_invoice_pdf_task(self, order_id):
    """Celery task to generate a PDF invoice by calling the InvoiceService."""
    logger.info(f"Executing invoice generation task id {self.request.id} for order {order_id}")
    with current_app.app_context():
        InvoiceService.generate_pdf(order_id)
    logger.info(f"Successfully generated invoice for order {order_id}")


@resilient_task
def generate_passport_pdf_task(self, passport_id):
    """Celery task to generate a product passport PDF by calling the PassportService."""
    logger.info(f"Executing passport generation task id {self.request.id} for passport {passport_id}")
    with current_app.app_context():
        PassportService.generate_pdf(passport_id)
    logger.info(f"Successfully generated passport for {passport_id}")


@resilient_task
def finalize_order_task(self, order_id):
    """
    Orchestration task to finalize an order after payment.
    It calls other tasks for invoice generation and confirmation emails.
    """
    logger.info(f"Executing 'finalize_order_task' for order {order_id}")
    with current_app.app_context():
        order = Order.query.get(order_id)
        if not order:
            logger.error(f"Order {order_id} not found in finalize_order_task.")
            return

        # Queue subsequent, independent jobs.
        generate_invoice_pdf_task.delay(order_id)
        
        user = order.user or order.b2b_user
        if not user:
             logger.error(f"No user found for order {order_id}.")
             return

        email_context = {'order_id': order.id, 'customer_name': user.first_name}
        send_email_task.delay(
            recipient=user.email,
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
    with current_app.app_context():
        OrderService.fulfill_order(order_id)


# --- Scheduled Tasks ---

@scheduled_task(name='tasks.clear_application_cache')
def clear_application_cache(self):
    """
    A periodic task to clear the entire Flask cache as a safety net.
    """
    with current_app.app_context():
        try:
            cache.clear()
            logger.info("Successfully cleared the application cache.")
            return "Cache cleared successfully."
        except Exception as e:
            logger.error(f"Failed to clear application cache: {e}")
            raise

@scheduled_task(name='tasks.update_all_user_tiers')
def update_all_user_tiers(self):
    """
    A periodic task that calls the loyalty service to recalculate and update
    the loyalty tier for all users (B2C and B2B).
    This should be run daily.
    """
    with current_app.app_context():
        logger.info("Starting scheduled user tier recalculation task.")
        try:
            # Assumes LoyaltyService has a method to update tiers for all users
            result_message = LoyaltyService.update_all_user_tiers_task()
            logger.info(f"Finished user tier recalculation task. Result: {result_message}")
            return result_message
        except Exception as e:
            logger.error(f"An error occurred during the scheduled tier recalculation: {e}", exc_info=True)
            raise

@scheduled_task(name='tasks.expire_loyalty_points')
def expire_loyalty_points_task(self):
    """Scheduled task to expire old loyalty points via LoyaltyService."""
    logger.info("Starting scheduled task: expire_loyalty_points_task")
    with current_app.app_context():
        count = LoyaltyService.expire_points_task()
    logger.info(f"Finished scheduled task: Expired {count} loyalty point transactions.")
    return f"Expired {count} loyalty point records."
