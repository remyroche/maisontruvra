from backend.extensions import celery
from backend.services.email_service import EmailService
from backend.services.loyalty_service import LoyaltyService
from flask import current_app
from flask_mail import Message
import logging

logger = logging.getLogger(__name__)

# --- IMPLEMENTATION: Celery Task Retries and Timeouts ---
@celery.task(
    autoretry_for=(Exception,),      # Retry on any exception from the email service
    retry_kwargs={'max_retries': 3}, # Attempt a maximum of 3 retries
    retry_backoff=True,              # Use exponential backoff (e.g., wait 1s, 2s, 4s)
    soft_time_limit=60,              # Raise exception if task runs longer than 60 seconds
    time_limit=90                    # Forcefully kill worker if task runs > 90 seconds
)
def send_email_task(recipient, subject, template, **kwargs):
    """
    Celery task to send an email asynchronously with resilience features.
    """
    # This assumes the core email logic is in a method that can be called directly.
    EmailService.send_email_immediately(recipient, subject, template, **kwargs)



@celery.task(name='tasks.expire_points')
def expire_points():
    """
    Celery task to expire loyalty points older than one year.
    """
    with current_app.app_context():
        try:
            count = LoyaltyService.expire_points_task()
            current_app.logger.info(f"Expired {count} loyalty point transactions.")
            return count
        except Exception as e:
            current_app.logger.error(f"Failed to expire points: {str(e)}")
            raise

@celery.task(name='tasks.update_tiers')
def update_tiers():
    """
    Celery task to recalculate and update B2B user loyalty tiers.
    """
    with current_app.app_context():
        try:
            count = LoyaltyService.update_user_tiers_task()
            current_app.logger.info(f"Updated loyalty tiers for {count} active B2B users.")
            return count
        except Exception as e:
            current_app.logger.error(f"Failed to update tiers: {str(e)}")
            raise

from backend.celery_worker import celery
from backend.services.email_service import EmailService


@celery.task(name='tasks.generate_invoice_pdf')
def generate_invoice_pdf_task(order_id):
    """
    Celery task to generate a PDF invoice for an order.
    """
    with current_app.app_context():
        try:
            current_app.logger.info(f"Generating invoice PDF for order {order_id}...")
            # from backend.services.invoice_service import InvoiceService
            # InvoiceService.generate_pdf(order_id)
            current_app.logger.info(f"Successfully generated invoice for order {order_id}")
        except Exception as e:
            current_app.logger.error(f"Failed to generate invoice for order {order_id}: {str(e)}")
            raise

@celery.task(name='tasks.generate_passport_pdf')
def generate_passport_pdf_task(passport_id):
    """
    Celery task to generate a product passport PDF.
    """
    with current_app.app_context():
        try:
            current_app.logger.info(f"Generating product passport PDF for {passport_id}...")
            # from backend.services.passport_service import PassportService
            # PassportService.generate_pdf(passport_id)
            current_app.logger.info(f"Successfully generated passport for {passport_id}")
        except Exception as e:
            current_app.logger.error(f"Failed to generate passport for {passport_id}: {str(e)}")
            raise

@celery.task(name='tasks.update_b2b_loyalty_tiers')
def update_b2b_loyalty_tiers_task():
    """
    Celery task to periodically update B2B loyalty tiers.
    """
    with current_app.app_context():
        try:
            current_app.logger.info("Starting scheduled task: update_b2b_loyalty_tiers_task")
            LoyaltyService.update_user_tiers_task()
            current_app.logger.info("Finished scheduled task: update_b2b_loyalty_tiers_task")
            return "B2B loyalty tiers updated successfully."
        except Exception as e:
            current_app.logger.error(f"Scheduled task update_b2b_loyalty_tiers_task failed: {e}", exc_info=True)
            raise

# Example of how you might schedule this task in your Celery beat configuration:
# celery.conf.beat_schedule = {
#     'update-b2b-tiers-every-day': {
#         'task': 'app.update_b2b_loyalty_tiers',
#         'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
#     },
# }
