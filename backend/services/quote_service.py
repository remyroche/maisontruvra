from datetime import datetime
import uuid
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from backend.extensions import db
from backend.models import Quote, QuoteItem, Invoice, B2BAccount
from backend.services.email_service import EmailService
from backend.services.pos_service import POSService
from backend.services.monitoring_service import MonitoringService
from backend.services.audit_log_service import AuditLogService
from backend.services.exceptions import NotFoundException, ValidationException, ServiceError
from backend.utils.input_sanitizer import InputSanitizer


class QuoteService:
    def __init__(self, logger):
        self.logger = logger
        self.email_service = EmailService(logger)
        self.pos_service = POSService(logger)
        # Assuming cart_service and product_service are available or injected elsewhere
        # self.cart_service = CartService(logger)
        # self.product_service = ProductService(logger)


    def create_quote_request(self, user_id, items_data):
        """Creates a new quote request for a B2B user."""
        try:
            quote = Quote(user_id=user_id, status='pending')
            db.session.add(quote)
            db.session.flush()

            for item in items_data:
                quote_item = QuoteItem(
                    quote_id=quote.id,
                    product_id=item['product_id'],
                    quantity=item['quantity']
                )
                db.session.add(quote_item)
            
            db.session.commit()
            self.logger.info(f"Quote request {quote.id} created for user {user_id}.")
            # TODO: Notify admin of new quote request
            return quote
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"Error creating quote request for user {user_id}: {e}")
            raise

    def get_quote_by_id(self, quote_id):
        return db.session.query(Quote).options(
            joinedload(Quote.items).joinedload(QuoteItem.product),
            joinedload(Quote.user)
        ).filter_by(id=quote_id).first()

    def respond_to_quote(self, quote_id, response_data):
        """Allows an admin to respond to a quote with custom prices."""
        try:
            quote = self.get_quote_by_id(quote_id)
            if not quote:
                raise ValueError("Quote not found.")

            for item_response in response_data['items']:
                quote_item = db.session.query(QuoteItem).filter_by(id=item_response['item_id'], quote_id=quote_id).first()
                if quote_item:
                    quote_item.response_price = item_response['price']

            quote.status = 'responded'
            quote.responded_at = datetime.utcnow()
            quote.set_expiry(days=response_data.get('valid_for_days', 7))
            db.session.commit()

            # Notify B2B user that their quote has a response
            # self.email_service.send_email(...)
            self.logger.info(f"Admin responded to quote {quote_id}.")
            return quote
        except (SQLAlchemyError, ValueError) as e:
            db.session.rollback()
            self.logger.error(f"Error responding to quote {quote_id}: {e}")
            raise

    def respond_and_add_to_cart(self, quote_id, response_data):
        """
        Admin responds to a quote. For custom items, it creates an exclusive
        product and adds it directly to the B2B user's cart.
        """
        try:
            quote = self.get_quote_by_id(quote_id)
            if not quote:
                raise ValueError("Quote not found.")
            
            user_id = quote.user_id

            for item_response in response_data['items']:
                quote_item = db.session.query(QuoteItem).filter_by(id=item_response['item_id'], quote_id=quote_id).first()
                if not quote_item:
                    continue

                price = item_response['price']
                quote_item.response_price = price
                
                product_id_to_add = quote_item.product_id

                # If it's a custom item, create the exclusive product now
                if quote_item.custom_item_name:
                    # This assumes product_service is available on self
                    exclusive_product = self.product_service.create_exclusive_product_for_quote(
                        name=quote_item.custom_item_name,
                        description=quote_item.custom_item_description,
                        price=price,
                        owner_id=user_id
                    )
                    product_id_to_add = exclusive_product.id
                
                # Add the item (existing or new) directly to the user's cart
                # This assumes cart_service is available on self
                self.cart_service.add_item_to_cart(
                    user_id=user_id,
                    product_id=product_id_to_add,
                    quantity=quote_item.quantity,
                    custom_price=price
                )

            quote.status = 'accepted' # The quote is now considered fulfilled
            quote.responded_at = datetime.utcnow()
            db.session.commit()

            # TODO: Notify B2B user that items have been added to their cart
            # self.email_service.send_email(...)
            
            self.logger.info(f"Admin responded to quote {quote_id} and added items directly to cart for user {user_id}.")
            return quote

        except (SQLAlchemyError, ValueError, PermissionError) as e:
            db.session.rollback()
            self.logger.error(f"Error in respond_and_add_to_cart for quote {quote_id}: {e}")
            raise

    @staticmethod
    def update_quote(quote_id, data):
        """Update a quote"""
        try:
            quote_id = InputSanitizer.sanitize_input(quote_id)
            
            quote = Quote.query.get(quote_id)
            if not quote:
                raise NotFoundException("Quote not found")
            
            # Update fields
            if 'total_amount' in data:
                quote.total_amount = float(InputSanitizer.sanitize_input(data['total_amount']))
            if 'notes' in data:
                quote.notes = InputSanitizer.sanitize_input(data['notes'])
            if 'status' in data:
                quote.status = InputSanitizer.sanitize_input(data['status'])
            
            quote.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            AuditLogService.log_action(
                user_id=None,  # System action
                action="UPDATE_QUOTE",
                resource_type="QUOTE",
                resource_id=quote.id,
                details=f"Updated quote {quote_id}"
            )
            
            MonitoringService.log_info(
                f"Updated quote {quote_id}",
                "QuoteService"
            )
            return quote
            
        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(f"Error updating quote {quote_id}: {str(e)}")
            raise ServiceError(f"Failed to update quote: {str(e)}")
    
    @staticmethod
    def delete_quote(quote_id):
        """Delete a quote"""
        try:
            quote_id = InputSanitizer.sanitize_input(quote_id)
            
            quote = Quote.query.get(quote_id)
            if not quote:
                return False
            
            if hasattr(quote, 'invoice') and quote.invoice:
                raise ValidationException("Cannot delete quote that has been converted to invoice")
            
            db.session.delete(quote)
            db.session.commit()
            
            AuditLogService.log_action(
                user_id=None,  # System action
                action="DELETE_QUOTE",
                resource_type="QUOTE",
                resource_id=quote_id,
                details=f"Deleted quote {quote_id}"
            )
            
            MonitoringService.log_info(
                f"Deleted quote {quote_id}",
                "QuoteService"
            )
            return True
            
        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(f"Error deleting quote {quote_id}: {str(e)}")
            raise ServiceError(f"Failed to delete quote: {str(e)}")
    
    @staticmethod
    def approve_quote(quote_id):
        """Approve a quote"""
        try:
            quote_id = InputSanitizer.sanitize_input(quote_id)
            
            quote = Quote.query.get(quote_id)
            if not quote:
                raise NotFoundException("Quote not found")
            
            if quote.status != 'pending':
                raise ValidationException("Quote is not in pending status")
            
            quote.status = 'approved'
            quote.approved_at = datetime.utcnow()
            
            db.session.commit()
            
            AuditLogService.log_action(
                user_id=None,  # System action
                action="APPROVE_QUOTE",
                resource_type="QUOTE",
                resource_id=quote.id,
                details=f"Approved quote {quote_id}"
            )
            
            MonitoringService.log_info(
                f"Approved quote {quote_id}",
                "QuoteService"
            )
            return quote
            
        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(f"Error approving quote {quote_id}: {str(e)}")
            raise ServiceError(f"Failed to approve quote: {str(e)}")
    
    @staticmethod
    def reject_quote(quote_id, reason=None):
        """Reject a quote"""
        try:
            quote_id = InputSanitizer.sanitize_input(quote_id)
            reason = InputSanitizer.sanitize_input(reason) if reason else None
            
            quote = Quote.query.get(quote_id)
            if not quote:
                raise NotFoundException("Quote not found")
            
            if quote.status != 'pending':
                raise ValidationException("Quote is not in pending status")
            
            quote.status = 'rejected'
            quote.rejected_at = datetime.utcnow()
            if reason:
                quote.rejection_reason = reason
            
            db.session.commit()
            
            AuditLogService.log_action(
                user_id=None,  # System action
                action="REJECT_QUOTE",
                resource_type="QUOTE",
                resource_id=quote.id,
                details=f"Rejected quote {quote_id}: {reason or 'No reason provided'}"
            )
            
            MonitoringService.log_info(
                f"Rejected quote {quote_id}",
                "QuoteService"
            )
            return quote
            
        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(f"Error rejecting quote {quote_id}: {str(e)}")
            raise ServiceError(f"Failed to reject quote: {str(e)}")
    
    @staticmethod
    def get_quotes_by_account(b2b_account_id):
        """Get all quotes for a B2B account"""
        try:
            b2b_account_id = InputSanitizer.sanitize_input(b2b_account_id)
            
            quotes = Quote.query.filter_by(b2b_account_id=b2b_account_id)\
                                 .order_by(Quote.created_at.desc()).all()
            return quotes
            
        except Exception as e:
            MonitoringService.log_error(f"Error getting quotes for account {b2b_account_id}: {str(e)}")
            raise ServiceError(f"Failed to get quotes: {str(e)}")
