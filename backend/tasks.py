# tasks.py
import logging
from flask import current_app
from backend.celery_worker import celery
from backend.services.email_service import EmailService
from backend.services.loyalty_service import LoyaltyService
from backend.services.invoice_service import InvoiceService
from backend.services.passport_service import PassportService

logger = logging.getLogger(__name__)

# Define a standard decorator for resilient, one-off tasks (e.g., triggered by user action)
resilient_task = celery.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3},
    retry_backoff=True,
    soft_time_limit=300,  # 5 minutes
    time_limit=600        # 10 minutes
)

# Define a standard decorator for scheduled (beat) tasks
# These typically should not retry indefinitely as they will run again on the next schedule.
scheduled_task = celery.task(
    bind=True,
    soft_time_limit=1800, # 30 minutes
    time_limit=3600       # 1 hour
)

@resilient_task
def send_email_task(self, recipient, subject, template_name, context):
    """
    Celery task to send an email asynchronously.
    """
    try:
        logger.info(f"Executing task id {self.request.id} for recipient {recipient}")
        with current_app.app_context(): # Ensure app context for render_template
            EmailService.send_email_immediately(recipient, subject, template_name, context)
    except Exception as e:
        logger.error(f"Task {self.request.id} failed: {e}", exc_info=True)
        raise

@resilient_task
def generate_invoice_pdf_task(self, order_id):
    """
    Celery task to generate a PDF invoice for an order.
    """
    try:
        logger.info(f"Executing invoice generation task id {self.request.id} for order {order_id}")
        with current_app.app_context():
            InvoiceService.generate_pdf(order_id)
        logger.info(f"Successfully generated invoice for order {order_id}")
    except Exception as e:
        logger.error(f"Task {self.request.id} failed to generate invoice for order {order_id}: {e}", exc_info=True)
        raise

@resilient_task
def generate_passport_pdf_task(self, passport_id):
    """
    Celery task to generate a product passport PDF.
    """
    try:
        logger.info(f"Executing passport generation task id {self.request.id} for passport {passport_id}")
        with current_app.app_context():
            PassportService.generate_pdf(passport_id)
        logger.info(f"Successfully generated passport for {passport_id}")
    except Exception as e:
        logger.error(f"Task {self.request.id} failed to generate passport for {passport_id}: {e}", exc_info=True)
        raise

@scheduled_task
def expire_loyalty_points_task(self):
    """
    Scheduled Celery task to expire loyalty points older than one year.
    """
    with current_app.app_context():
        try:
            logger.info("Starting scheduled task: expire_loyalty_points_task")
            count = LoyaltyService.expire_points_task()
            logger.info(f"Finished scheduled task: Expired {count} loyalty point transactions.")
            return f"Expired {count} loyalty point records."
        except Exception as e:
            logger.error(f"Scheduled task expire_loyalty_points_task failed: {e}", exc_info=True)
            raise

@scheduled_task
def update_all_b2b_loyalty_tiers(self):
    """
    Scheduled task to recalculate and update all B2B user loyalty tiers.
    This replaces the previous redundant tasks.
    """
    with current_app.app_context():
        try:
            logger.info("Starting scheduled task: update_all_b2b_loyalty_tiers")
            count = LoyaltyService.update_user_tiers_task()
            logger.info(f"Finished scheduled task: Updated loyalty tiers for {count} active B2B users.")
            return f"Updated {count} B2B loyalty tiers."
        except Exception as e:
            logger.error(f"Scheduled task update_all_b2b_loyalty_tiers failed: {e}", exc_info=True)
            raise
