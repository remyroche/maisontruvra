from ..models import db, StockNotification, Product, User
from .exceptions import ServiceError, NotFoundException
from flask import current_app

class NotificationService:
    @staticmethod
    def create_stock_notification(product_id: int, user_id: int = None, guest_email: str = None):
        """Creates a request to be notified when a product is back in stock."""
        product = Product.query.get(product_id)
        if not product:
            raise NotFoundException("Product not found.")

        # Check if a notification already exists and is pending
        query = StockNotification.query.filter_by(product_id=product_id, notified=False)
        if user_id:
            existing_notification = query.filter_by(user_id=user_id).first()
        elif guest_email:
            existing_notification = query.filter_by(guest_email=guest_email).first()
        else: # Should not happen with proper frontend logic
             raise ServiceError("User or email required.", 400)

        if existing_notification:
            raise ServiceError("You are already on the waiting list for this product.", 409)

        new_notification = StockNotification(product_id=product_id, user_id=user_id, guest_email=guest_email)
        db.session.add(new_notification)
        db.session.commit()
        current_app.logger.info(f"Stock notification created for product {product_id} for user {user_id or guest_email}")
        return new_notification

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
