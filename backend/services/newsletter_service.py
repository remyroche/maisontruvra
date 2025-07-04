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
        # TODO: Implement newsletter subscriber model and logic
        return {"subscribers": [], "total": 0, "pages": 0, "current_page": page}

    @staticmethod
    def send_campaign(subject, content, subscriber_ids=None):
        """Send a newsletter campaign."""
        # TODO: Implement newsletter campaign sending logic
        logger.info(f"Newsletter campaign '{subject}' sending requested")
        return True
