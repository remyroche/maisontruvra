from flask_mail import Mail
from celery import Celery
from flask_caching import Cache

mail = Mail()
celery = Celery(__name__, broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
cache = Cache()
