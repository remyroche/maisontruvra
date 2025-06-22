from backend.extensions import celery
from backend.services.email_service import EmailService
from backend.services.b2b_loyalty_service import B2BLoyaltyService
from flask import current_app

@celery.task(name='app.send_email')
def send_email_task(to, subject, template, **kwargs):
    """
    Celery task to send an email asynchronously.
    """
    try:
        EmailService.send_email(to, subject, template, **kwargs)
        return f"Email sent to {to} with subject '{subject}'"
    except Exception as e:
        current_app.logger.error(f"Failed to send email to {to}: {e}", exc_info=True)
        # Retry the task, for example, after 10 minutes, for a maximum of 3 times.
        raise send_email_task.retry(exc=e, countdown=600, max_retries=3)

@celery.task(name='app.update_b2b_loyalty_tiers')
def update_b2b_loyalty_tiers_task():
    """
    Celery task to periodically update B2B loyalty tiers.
    """
    try:
        current_app.logger.info("Starting scheduled task: update_b2b_loyalty_tiers_task")
        B2BLoyaltyService._calculate_and_assign_tiers()
        current_app.logger.info("Finished scheduled task: update_b2b_loyalty_tiers_task")
        return "B2B loyalty tiers updated successfully."
    except Exception as e:
        current_app.logger.error(f"Scheduled task update_b2b_loyalty_tiers_task failed: {e}", exc_info=True)
        raise update_b2b_loyalty_tiers_task.retry(exc=e, countdown=3600) # Retry after 1 hour

# Example of how you might schedule this task in your Celery beat configuration:
# celery.conf.beat_schedule = {
#     'update-b2b-tiers-every-day': {
#         'task': 'app.update_b2b_loyalty_tiers',
#         'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
#     },
# }
