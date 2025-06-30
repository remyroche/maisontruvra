from backend.extensions import db
from backend.models.product_models import Product, StockNotificationRequest
from backend.models.user_models import User
from backend.models.utility_models import StockNotification
from .monitoring_service import MonitoringService
from .exceptions import ServiceError, NotFoundException, ValidationException
from flask import current_app
from ..tasks import send_back_in_stock_email_task
from backend.services.email_service import send_email

class NotificationService:

    def notify_user_of_loyalty_points(user_id, points):
        """Notifies a user that they have received loyalty points."""
        user = User.query.get(user_id)
        if not user:
            current_app.logger.warning(f"Could not send loyalty notification to user {user_id}. User not found.")
            return

        try:
            # This can be expanded to include other notification types (e.g., push notifications)
            send_email(
                to=user.email,
                subject="Vous avez gagné des points de fidélité !",
                template="emails/loyalty_points_notification.html", # Assuming this template exists
                user=user,
                points=points
            )
            current_app.logger.info(f"Sent loyalty points notification to {user.email}.")
        except Exception as e:
            current_app.logger.error(f"Failed to send loyalty notification to {user.email}: {e}")

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
    def send_back_in_stock_notification(user: User, product_name: str):
        """
        Queues a 'back in stock' email notification.
        """
        try:
            # Import task here to prevent circular imports
            from ..tasks import send_back_in_stock_email_task
            send_back_in_stock_email_task.delay(user.id, product_name)
            MonitoringService.log_info(f"Queued back-in-stock notification for product '{product_name}' to user {user.email}")
        except Exception as e:
            MonitoringService.log_info(f"Failed to queue back-in-stock email: {e}", exc_info=True)
            
    @staticmethod
    def send_tier_upgrade_notification(user: User, new_tier_name: str):
        """
        Queues a loyalty tier upgrade notification.
        """
        try:
            # Import task here to prevent circular imports
            from ..tasks import send_tier_upgrade_email_task
            send_tier_upgrade_email_task.delay(user.id, new_tier_name)
            MonitoringService.log_info(f"Queued tier upgrade notification for user {user.email} to tier {new_tier_name}")
        except Exception as e:
            MonitoringService.log_info(f"Failed to queue tier upgrade email: {e}", exc_info=True)


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
        MonitoringService.log_info(
            f"Cleared {len(subscribers)} stock notifications for product {product_id}",
            "NotificationService"
        )
        return subscribers
