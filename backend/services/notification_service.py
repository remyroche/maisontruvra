import logging

from backend.extensions import db
from backend.models.product_models import StockNotificationRequest
from backend.models.user_models import User
from backend.models.utility_models import StockNotification

from .exceptions import ValidationException
from .monitoring_service import MonitoringService

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, session=None):
        self.session = session or db.session
        self.logger = logger

    def send_loyalty_points_notification(self, user_id, points_earned):
        """
        Queues a background task to notify a user they have earned loyalty points.
        """
        if not user_id or points_earned <= 0:
            return

        self.logger.info(f"Queueing loyalty points notification for user {user_id}.")
        # Delegate the email sending to a dedicated Celery task
        from ..tasks import send_loyalty_points_email_task

        send_loyalty_points_email_task.delay(user_id, points_earned)

    def send_order_confirmation(self, order_id):
        """Queues a task to send an order confirmation email."""
        self.logger.info(f"Queueing order confirmation email for order ID: {order_id}")
        send_order_confirmation_email_task.delay(order_id)

    def send_order_status_update(self, order_id, new_status):
        """Queues a task to send an order status update email."""
        self.logger.info(
            f"Queueing status update email for order {order_id} to '{new_status}'"
        )
        send_order_status_update_task.delay(order_id, new_status)

    def notify_users_of_restock(self, product_id):
        """
        Finds all subscribed users and queues a task to notify them of a restock.
        """
        subscribers = (
            self.session.query(StockNotificationRequest)
            .filter_by(product_id=product_id, notified=False)
            .all()
        )

        if not subscribers:
            return

        user_ids = [sub.user_id for sub in subscribers]
        send_back_in_stock_notifications_task.delay(
            user_ids=user_ids, product_id=product_id
        )

        for sub in subscribers:
            sub.notified = True
        self.session.commit()
        self.logger.info(
            f"Queued back-in-stock notifications for {len(user_ids)} users for product {product_id}."
        )

    @staticmethod
    def create_stock_notification_request(user_id, product_id):
        """Creates a request for a user to be notified when a product is back in stock."""
        existing_request = StockNotificationRequest.query.filter_by(
            user_id=user_id, product_id=product_id
        ).first()
        if existing_request:
            raise ValidationException(
                "You are already subscribed to notifications for this product."
            )

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
            MonitoringService.log_info(
                f"Queued back-in-stock notification for product '{product_name}' to user {user.email}"
            )
        except Exception as e:
            MonitoringService.log_info(
                f"Failed to queue back-in-stock email: {e}", exc_info=True
            )

    @staticmethod
    def send_tier_upgrade_notification(user: User, new_tier_name: str):
        """
        Queues a loyalty tier upgrade notification.
        """
        try:
            # Import task here to prevent circular imports
            from ..tasks import send_tier_upgrade_email_task

            send_tier_upgrade_email_task.delay(user.id, new_tier_name)
            MonitoringService.log_info(
                f"Queued tier upgrade notification for user {user.email} to tier {new_tier_name}"
            )
        except Exception as e:
            MonitoringService.log_info(
                f"Failed to queue tier upgrade email: {e}", exc_info=True
            )

    def send_loyalty_points_notification(self, user_id, points_earned):
        """
        Prepares and sends an email to the user about newly earned loyalty points.
        """
        try:
            user = self.user_service.get_user_by_id(user_id)
            if not user or not user.email:
                logger.warning(
                    f"User with ID {user_id} not found or has no email for loyalty notification."
                )
                return

            # Ensure the user has a loyalty account to get the total points
            total_points = (
                user.loyalty_account.points
                if hasattr(user, "loyalty_account") and user.loyalty_account
                else points_earned
            )

            subject = "Vous avez gagné des points de fidélité !"
            template = "emails/loyalty_points_notification.html"
            context = {
                "user_name": user.first_name,
                "points_earned": points_earned,
                "total_points": total_points,
            }

            self.email_service.send_email(
                to=user.email, subject=subject, template=template, context=context
            )
            logger.info(
                f"Successfully queued loyalty points notification for user {user.email}"
            )

        except Exception as e:
            logger.error(
                f"Failed to send loyalty points notification for user ID {user_id}: {e}",
                exc_info=True,
            )

    @staticmethod
    def trigger_back_in_stock_notifications(product_id):
        """Finds all requests for a product and triggers email tasks."""
        requests = StockNotificationRequest.query.filter_by(product_id=product_id).all()
        if not requests:
            return

        user_ids = [req.user_id for req in requests]
        send_back_in_stock_notifications_task.delay(user_ids, product_id)

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
        notifications = (
            StockNotification.query.filter_by(product_id=product_id, notified=False)
            .with_for_update()
            .all()
        )

        if not notifications:
            return []

        subscribers = []
        for n in notifications:
            email = n.user.email if n.user else n.guest_email
            name = n.user.first_name if n.user else "cher client"
            if email:
                subscribers.append({"email": email, "name": name})
            # Mark as notified to prevent re-sending
            n.notified = True

        db.session.commit()
        MonitoringService.log_info(
            f"Cleared {len(subscribers)} stock notifications for product {product_id}",
            "NotificationService",
        )
        return subscribers
