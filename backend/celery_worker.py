from celery import Celery
from celery.schedules import crontab
import logging

# Set up logger for this module
logger = logging.getLogger(__name__)

# Instantiate Celery.
# The configuration will be loaded from the Flask app config in create_app.
celery = Celery(__name__)

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Sets up the schedule for all periodic background tasks.
    The task names are strings that celery uses to find the task functions.
    Make sure they match the actual paths to your tasks.
    """
    logger.info("Setting up periodic tasks...")
    
    # Daily B2B Tier Recalculation Task
    sender.add_periodic_task(
        crontab(hour=0, minute=0), # Executes daily at midnight
        'tasks.update_all_user_tiers',
        name='Update B2B loyalty tiers daily'
    )
    
    # Periodic Cache Clear Task
    sender.add_periodic_task(
        crontab(hour='*/6'), # Executes every 6 hours
        'tasks.clear_application_cache',
        name='Clear application cache every 6 hours'
    )
    logger.info("Periodic tasks set up.")
