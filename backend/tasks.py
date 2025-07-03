# backend/tasks.py

import logging
import os
from flask import current_app

from .celery_worker import celery_app
from .extensions import cache

# Configure a logger for this file
logger = logging.getLogger(__name__)

# ==============================================================================
# 1. USER-FACING & TRANSACTIONAL TASKS
#    (Tasks triggered directly by user actions like placing an order)
# ==============================================================================

@celery_app.task(name='tasks.finalize_order', bind=True, max_retries=3, default_retry_delay=60)
def finalize_order_task(self, order_id):
    """
    Orchestration task to finalize an order after payment.
    It calls other tasks for invoice generation and confirmation emails.
    """
    from .services.order_service import OrderService
    from .services.notification_service import NotificationService

    logger.info(f"Executing 'finalize_order_task' for order ID: {order_id}")
    try:
        order_service = OrderService()
        order = order_service.get_order_by_id(order_id)
        if not order:
            logger.error(f"Order {order_id} not found in finalize_order_task.")
            return

        # Queue subsequent, independent jobs.
        generate_invoice_pdf_task.delay(order.invoice.id)
        send_order_confirmation_email_task.delay(order.id)
        
    except Exception as exc:
        logger.error(f"Error in finalize_order_task for order {order_id}: {exc}", exc_info=True)
        self.retry(exc=exc)


@celery_app.task(name='tasks.generate_invoice_pdf', bind=True, max_retries=3, default_retry_delay=60)
def generate_invoice_pdf_task(self, invoice_id):
    """Celery task to generate a PDF invoice by calling the InvoiceService."""
    from .services.invoice_service import InvoiceService
    
    logger.info(f"Starting PDF generation for Invoice ID: {invoice_id}")
    try:
        invoice_service = InvoiceService()
        invoice_service.generate_invoice_pdf(invoice_id)
        logger.info(f"Successfully generated PDF for invoice {invoice_id}")
    except Exception as exc:
        logger.error(f"Failed to generate PDF for invoice {invoice_id}: {exc}", exc_info=True)
        self.retry(exc=exc)


@celery_app.task(name="tasks.send_back_in_stock_notifications")
def send_back_in_stock_notifications_task(user_ids, product_id):
    """Sends notification emails to a list of users for a specific product."""
    from .services.notification_service import NotificationService
    notification_service = NotificationService()
    notification_service.send_back_in_stock_notifications(user_ids, product_id)
    return f"Back-in-stock notifications queued for {len(user_ids)} users for product {product_id}"

@celery_app.task(name="tasks.send_order_confirmation_email")
def send_order_confirmation_email_task(order_id):
    """Queues the sending of an order confirmation email."""
    from .services.notification_service import NotificationService
    notification_service = NotificationService()
    notification_service.send_order_confirmation(order_id)
    return f"Order confirmation email task queued for order ID: {order_id}"


@celery_app.task(name="tasks.send_order_confirmation_email")
def send_b2b_order_confirmation_email_task(order_id):
    """Queues the sending of an order confirmation email."""
    from .services.notification_service import NotificationService
    notification_service = NotificationService()
    notification_service.send_b2b_order_confirmation(order_id)
    return f"Order confirmation email task queued for order ID: {order_id}"

# ** FIX: Add the missing task definition **
@celery_app.task(name="tasks.send_order_status_update")
def send_order_status_update_task(order_id, new_status):
    """
    Asynchronous task to send an email when an order's status is updated.
    """
    from .services.notification_service import NotificationService
    logger.info(f"Executing status update email task for order {order_id} to status '{new_status}'.")
    notification_service = NotificationService()
    notification_service.send_order_status_update(order_id, new_status)
    return f"Order status update email task queued for order {order_id}."

@celery_app.task(name='tasks.process_b2b_quick_order', bind=True, max_retries=3, default_retry_delay=60)
def process_b2b_quick_order_task(self, b2b_user_id, file_content_str):
    """
    Processes a B2B quick order from a CSV file content string.
    """
    from .services.b2b_service import B2BService
    
    logger.info(f"Starting B2B quick order processing for user {b2b_user_id}.")
    try:
        b2b_service = B2BService()
        b2b_service.create_order_from_csv(b2b_user_id, file_content_str)
    except Exception as exc:
        logger.error(f"Failed to process B2B quick order for user {b2b_user_id}: {exc}", exc_info=True)
        # Here you might want to notify the user of the final failure
        self.retry(exc=exc)

# ==============================================================================
# 2. SCHEDULED & MAINTENANCE TASKS
#    (Tasks run on a schedule by Celery Beat)
# ==============================================================================

@celery_app.task(name='tasks.clear_application_cache', bind=True)
def clear_application_cache_task(self):
    """A periodic task to clear the entire Flask cache."""
    logger.info("Starting scheduled cache clearing task.")
    try:
        with current_app.app_context():
            cache.clear()
        logger.info("Successfully cleared the application cache.")
        return "Cache cleared successfully."
    except Exception as e:
        logger.error(f"Failed to clear application cache: {e}", exc_info=True)
        raise  # Re-raise to have Celery mark it as failed

@celery_app.task(name='tasks.update_all_user_tiers', bind=True)
def update_all_user_tiers_task(self):
    """
    A periodic task that recalculates and updates the loyalty tier for all users.
    """
    from .services.loyalty_service import LoyaltyService
    
    logger.info("Starting scheduled user tier recalculation task.")
    try:
        loyalty_service = LoyaltyService()
        result_message = loyalty_service.update_all_user_tiers()
        logger.info(f"Finished user tier recalculation task. Result: {result_message}")
        return result_message
    except Exception as e:
        logger.error(f"An error occurred during scheduled tier recalculation: {e}", exc_info=True)
        raise

@celery_app.task(name='tasks.expire_loyalty_points', bind=True)
def expire_loyalty_points_task(self):
    """Scheduled task to expire old loyalty points."""
    from .services.loyalty_service import LoyaltyService
    
    logger.info("Starting scheduled task: expire_loyalty_points_task")
    try:
        loyalty_service = LoyaltyService()
        count = loyalty_service.expire_points()
        logger.info(f"Finished scheduled task: Expired {count} loyalty point transactions.")
        return f"Expired {count} loyalty point records."
    except Exception as e:
        logger.error(f"An error occurred during loyalty point expiration: {e}", exc_info=True)
        raise


@celery_app.task(name="tasks.update_inventory_on_order")
def update_inventory_on_order_task(product_id, quantity_ordered):
    """
    Celery task to update inventory after an order is placed.
    """
    from .services.inventory_service import InventoryService
    logger.info(f"Executing update_inventory_on_order_task for product_id: {product_id}, quantity: {quantity_ordered}")
    try:
        inventory_service = InventoryService()
        inventory_service.decrease_stock(product_id, quantity_ordered)
    except Exception as e:
        logger.error(f"Error in update_inventory_on_order_task for product {product_id}: {e}", exc_info=True)

@celery_app.task(name="tasks.notify_user_of_loyalty_points")
def notify_user_of_loyalty_points_task(user_id, points_earned):
    """
    Celery task to notify a user about earned loyalty points.
    """
    from .services.notification_service import NotificationService
    logger.info(f"Executing notify_user_of_loyalty_points_task for user_id: {user_id} with {points_earned} points.")
    try:
        # Instantiate services within the task to ensure they run
        # in the Celery worker's application context.
        notification_service = NotificationService()
        notification_service.send_loyalty_points_notification(user_id, points_earned)
    except Exception as e:
        # Log any exceptions that occur within the task
        logger.error(f"Error in notify_user_of_loyalty_points_task for user_id {user_id}: {e}", exc_info=True)
