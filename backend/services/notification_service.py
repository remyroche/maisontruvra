from backend.database import db
from backend.models.product_models import Product
from backend.models.user_models import User
from backend.models.inventory_models import StockNotification
from .exceptions import ServiceError, NotFoundException
from flask import current_app
from ..models import StockNotificationRequest
from ..tasks import send_back_in_stock_email_task


class NotificationService:
    @staticmethod
    def create_stock_notification_request(user_id, product_id):
        """Creates a request for a user to be notified when a product is back in stock."""
        existing_request = StockNotificationRequest.query.filter_by(user_id=user_id, product_id=product_id).first()
        if existing_request:
            raise ValidationException("You are already subscribed to notifications for this product.")
        
        new_request = StockNotificationRequest(user_id=user_id, product_id=product_id)
        db.session.add(new_request)
        db.session.commit()
        return new_request


    @staticmethod
    def trigger_back_in_stock_notifications(product_id):
        """Finds all requests for a product and triggers email tasks."""
        requests = StockNotificationRequest.query.filter_by(product_id=product_id).all()
        if not requests:
            return

        user_ids = [req.user_id for req in requests]
        send_back_in_stock_email_task.delay(user_ids, product_id)

        # Delete the requests after queuing the emails
        for req in requests:
            db.session.delete(req)
        db.session.commit()

    
    @staticmethod
    def get_and_clear_stock_notifications(product_id: int):
        """
        Atomically retrieves all pending notifications for a product and marks them as handled.
        This prevents sending duplicate emails in case of multiple restocks.
        """
        # Using with_for_update() locks the selected rows until the transaction is committed.
        notifications = StockNotification.query.filter_by(
            product_id=product_id, 
            notified=False
        ).with_for_update().all()
        
        if not notifications:
            return []

        subscribers = []
        for n in notifications:
            email = n.user.email if n.user else n.guest_email
            name = n.user.first_name if n.user else 'cher client'
            if email:
                subscribers.append({'email': email, 'name': name})
            # Mark as notified to prevent re-sending
            n.notified = True
        
        db.session.commit()
        current_app.logger.info(f"Cleared {len(subscribers)} stock notifications for product {product_id}")
        return subscribers
