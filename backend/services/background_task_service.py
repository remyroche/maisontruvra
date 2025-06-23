
from backend.celery_worker import celery
from backend.database import db
from backend.models.order_models import Order
from backend.models.user_models import User
from backend.services.email_service import EmailService
from backend.services.invoice_service import InvoiceService
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class BackgroundTaskService:
    @staticmethod
    def queue_order_processing(order_id: int):
        """Queue order processing tasks."""
        try:
            # Queue the main order fulfillment task
            celery.send_task('fulfill_order', args=[order_id])
            
            # Queue invoice generation
            celery.send_task('generate_invoice', args=[order_id])
            
            # Queue order confirmation email
            celery.send_task('send_email', args=[{
                'type': 'order_confirmation',
                'order_id': order_id
            }])
            
            logger.info(f"Background tasks queued for order {order_id}")
            
        except Exception as e:
            logger.error(f"Failed to queue background tasks for order {order_id}: {str(e)}")
            raise
    
    @staticmethod
    def queue_user_welcome_email(user_id: int):
        """Queue welcome email for new user."""
        try:
            celery.send_task('send_email', args=[{
                'type': 'welcome',
                'user_id': user_id
            }])
            
            logger.info(f"Welcome email queued for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to queue welcome email for user {user_id}: {str(e)}")
    
    @staticmethod
    def queue_inventory_sync(product_variant_id: int):
        """Queue inventory synchronization task."""
        try:
            celery.send_task('sync_inventory', args=[product_variant_id])
            
            logger.info(f"Inventory sync queued for variant {product_variant_id}")
            
        except Exception as e:
            logger.error(f"Failed to queue inventory sync for variant {product_variant_id}: {str(e)}")
    
    @staticmethod
    def queue_low_stock_alert():
        """Queue low stock alert task."""
        try:
            celery.send_task('check_low_stock')
            
            logger.info("Low stock check task queued")
            
        except Exception as e:
            logger.error(f"Failed to queue low stock check: {str(e)}")
