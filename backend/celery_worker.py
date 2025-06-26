from backend import create_app, celery
from celery import Celery
import logging

# Set up logger for this module
logger = logging.getLogger(__name__)

def init_celery(app):
    """
    Initializes and configures the Celery instance with the Flask app's settings.
    Also, it wraps tasks to ensure they run within a Flask application context.
    
    Args:
        app: The configured Flask application instance.
    """
    # Update the Celery configuration from the Flask app config.
    # It will automatically look for keys starting with 'CELERY_'.
    celery.config_from_object(app.config, namespace='CELERY')

    class ContextTask(celery.Task):
        """
        A custom Celery Task class that ensures every task is executed
        within a Flask application context. This is crucial for accessing
        the database, configuration, and other Flask extensions within tasks.
        """
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    # Set the custom ContextTask as the default Task class for this Celery instance.
    celery.Task = ContextTask
    
    # This line is important for Celery's auto-discovery of tasks.
    # It tells Celery to look for task definitions in 'backend/tasks.py'.
    celery.autodiscover_tasks(['backend.tasks'])

    return celery

# The following lines are necessary to run the worker from the command line.
# It creates a Flask app instance to provide context for Celery.
app = create_app()
app.app_context().push()
