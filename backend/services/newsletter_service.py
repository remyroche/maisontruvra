"""
Newsletter Service for managing newsletter subscriptions and campaigns.
"""

import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.database import db
from backend.extensions import db
from backend.models import NewsletterSubscription, db
from backend.services.email_service import EmailService

logger = logging.getLogger(__name__)


class NewsletterService:
    """Service for managing newsletter subscriptions and campaigns."""

    def __init__(self, logger):
        self.logger = logger
        self.email_service = EmailService(logger)

    def subscribe(self, email, source="b2c"):
        """
        Subscribes an email to the newsletter.
        """
        try:
            # Check if already subscribed
            if db.session.query(NewsletterSubscription).filter_by(email=email).first():
                self.logger.warning(
                    f"Email {email} is already subscribed to the newsletter."
                )
                return None, "Email is already subscribed."

            subscription = NewsletterSubscription(email=email, source=source)
            db.session.add(subscription)
            db.session.commit()

            # Send confirmation email
            subject = "Subscription Confirmed"
            template = (
                "b2c_newsletter_confirmation"
                if source == "b2c"
                else "b2b_newsletter_confirmation"
            )
            context = {"email": email}
            self.email_service.send_email(email, subject, template, context)

            self.logger.info(f"Email {email} subscribed to the {source} newsletter.")
            return subscription, "Successfully subscribed."

        except IntegrityError:
            db.session.rollback()
            self.logger.warning(
                f"Attempt to subscribe existing email {email} failed due to constraint."
            )
            return None, "Email is already subscribed."
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(
                f"Database error during newsletter subscription for {email}: {e}"
            )
            raise

    def unsubscribe(self, email):
        """
        Unsubscribes an email from the newsletter.
        """
        try:
            subscription = (
                db.session.query(NewsletterSubscription).filter_by(email=email).first()
            )
            if subscription:
                db.session.delete(subscription)
                db.session.commit()
                self.logger.info(f"Email {email} unsubscribed from the newsletter.")
                return True
            else:
                self.logger.warning(
                    f"Attempt to unsubscribe non-existent email: {email}"
                )
                return False
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(
                f"Error during newsletter unsubscription for {email}: {e}"
            )
            raise

    @staticmethod
    def get_all_subscribers(page=1, per_page=20):
        """Get all newsletter subscribers with pagination."""
        try:
            query = db.session.query(NewsletterSubscription).filter_by(is_active=True)
            total = query.count()
            
            # Calculate pagination
            offset = (page - 1) * per_page
            subscribers = query.offset(offset).limit(per_page).all()
            pages = (total + per_page - 1) // per_page
            
            return {
                "subscribers": [sub.to_dict() for sub in subscribers],
                "total": total,
                "pages": pages,
                "current_page": page,
                "per_page": per_page
            }
        except SQLAlchemyError as e:
            logger.error(f"Error fetching newsletter subscribers: {e}")
            return {"subscribers": [], "total": 0, "pages": 0, "current_page": page}

    @staticmethod
    def send_campaign(subject, content, subscriber_ids=None, list_type=None):
        """Send a newsletter campaign."""
        try:
            # Build query for subscribers
            query = db.session.query(NewsletterSubscription).filter_by(is_active=True)
            
            if list_type:
                query = query.filter_by(list_type=list_type)
            
            if subscriber_ids:
                query = query.filter(NewsletterSubscription.id.in_(subscriber_ids))
            
            subscribers = query.all()
            
            if not subscribers:
                logger.warning("No subscribers found for campaign")
                return False
            
            # Send emails to all subscribers
            email_service = EmailService(logger)
            success_count = 0
            
            for subscriber in subscribers:
                try:
                    email_service.send_email(
                        subscriber.email,
                        subject,
                        "newsletter_campaign",
                        {"content": content, "subscriber": subscriber.to_dict()}
                    )
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to send email to {subscriber.email}: {e}")
            
            logger.info(f"Newsletter campaign '{subject}' sent to {success_count}/{len(subscribers)} subscribers")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error sending newsletter campaign: {e}")
            return False

    @staticmethod
    def get_subscriber_by_id(subscriber_id):
        """Get a specific subscriber by ID."""
        return db.session.query(NewsletterSubscription).get(subscriber_id)

    @staticmethod
    def delete_subscriber_by_id(subscriber_id):
        """Delete a subscriber by ID."""
        try:
            subscriber = db.session.query(NewsletterSubscription).get(subscriber_id)
            if subscriber:
                db.session.delete(subscriber)
                db.session.commit()
                logger.info(f"Subscriber {subscriber_id} deleted")
                return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error deleting subscriber {subscriber_id}: {e}")
            return False

    @staticmethod
    def get_subscriber_stats():
        """Get newsletter subscription statistics."""
        try:
            total_subscribers = db.session.query(NewsletterSubscription).filter_by(is_active=True).count()
            b2c_subscribers = db.session.query(NewsletterSubscription).filter_by(
                is_active=True, list_type="b2c"
            ).count()
            b2b_subscribers = db.session.query(NewsletterSubscription).filter_by(
                is_active=True, list_type="b2b"
            ).count()
            
            return {
                "total_subscribers": total_subscribers,
                "b2c_subscribers": b2c_subscribers,
                "b2b_subscribers": b2b_subscribers
            }
        except SQLAlchemyError as e:
            logger.error(f"Error getting subscriber stats: {e}")
            return {"total_subscribers": 0, "b2c_subscribers": 0, "b2b_subscribers": 0}
