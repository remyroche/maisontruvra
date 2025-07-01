from backend.database import db
from backend.models.invoice_models import Quote, Invoice
from backend.models.b2b_models import B2BAccount
from backend.services.monitoring_service import MonitoringService
from backend.services.exceptions import NotFoundException, ValidationException, ServiceError
from backend.utils.input_sanitizer import InputSanitizer
from backend.services.audit_log_service import AuditLogService
from flask import current_app
from datetime import datetime
import uuid


class QuoteService:
    """Service for managing quotes and quote requests"""
    
    def __init__(self, session=None):
        self.session = session or db.session
    
    @staticmethod
    def get_all_quotes():
        """Get all quotes"""
        try:
            quotes = Quote.query.order_by(Quote.created_at.desc()).all()
            return quotes
        except Exception as e:
            MonitoringService.log_error(f"Error getting all quotes: {str(e)}")
            raise ServiceError(f"Failed to get quotes: {str(e)}")
    
    @staticmethod
    def get_all_quotes_paginated(page=1, per_page=20, filters=None):
        """Get paginated quotes with optional filters"""
        try:
            query = Quote.query
            
            if filters:
                if filters.get('status'):
                    query = query.filter(Quote.status == filters['status'])
                if filters.get('b2b_account_id'):
                    query = query.filter(Quote.b2b_account_id == filters['b2b_account_id'])
                if filters.get('date_from'):
                    query = query.filter(Quote.created_at >= filters['date_from'])
                if filters.get('date_to'):
                    query = query.filter(Quote.created_at <= filters['date_to'])
            
            pagination = query.order_by(Quote.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'quotes': pagination.items,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': pagination.page,
                'per_page': pagination.per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        except Exception as e:
            MonitoringService.log_error(f"Error getting paginated quotes: {str(e)}")
            raise ServiceError(f"Failed to get quotes: {str(e)}")
    
    @staticmethod
    def get_quote_by_id(quote_id):
        """Get a quote by ID"""
        try:
            quote_id = InputSanitizer.InputSanitizer.sanitize_input(quote_id)
            quote = Quote.query.get(quote_id)
            if not quote:
                raise NotFoundException("Quote not found")
            return quote
        except Exception as e:
            MonitoringService.log_error(f"Error getting quote {quote_id}: {str(e)}")
            raise ServiceError(f"Failed to get quote: {str(e)}")
    
    def create_quote_request(self, user_id, items_data):
        """Creates a new quote request for a B2B user."""
        try:
            quote = Quote(user_id=user_id, status='pending')
            session.add(quote)
            session.flush()

            for item in items_data:
                quote_item = QuoteItem(
                    quote_id=quote.id,
                    product_id=item['product_id'],
                    quantity=item['quantity']
                )
                session.add(quote_item)
            
            session.commit()
            self.logger.info(f"Quote request {quote.id} created for user {user_id}.")
            # TODO: Notify admin of new quote request
            return quote
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"Error creating quote request for user {user_id}: {e}")
            raise

    def respond_to_quote(self, quote_id, response_data):
        """Allows an admin to respond to a quote with custom prices."""
        try:
            quote = self.get_quote_by_id(quote_id)
            if not quote:
                raise ValueError("Quote not found.")

            for item_response in response_data['items']:
                quote_item = session.query(QuoteItem).filter_by(id=item_response['item_id'], quote_id=quote_id).first()
                if quote_item:
                    quote_item.response_price = item_response['price']

            quote.status = 'responded'
            quote.responded_at = datetime.utcnow()
            quote.set_expiry(days=response_data.get('valid_for_days', 7))
            session.commit()

            # Notify B2B user that their quote has a response
            # self.email_service.send_email(...)
            self.logger.info(f"Admin responded to quote {quote_id}.")
            return quote
        except (SQLAlchemyError, ValueError) as e:
            session.rollback()
            self.logger.error(f"Error responding to quote {quote_id}: {e}")
            raise

    def accept_quote_and_create_cart(self, quote_id, user_id):
        """
        Accepts a quote and creates a new cart with custom-priced items.
        """
        try:
            quote = self.get_quote_by_id(quote_id)
            if not quote or quote.user_id != user_id:
                raise ValueError("Quote not found or access denied.")
            if quote.status != 'responded':
                raise ValueError("Quote cannot be accepted in its current state.")
            if quote.expires_at and quote.expires_at < datetime.utcnow():
                quote.status = 'expired'
                session.commit()
                raise ValueError("This quote has expired.")

            # Create a new cart for the user
            cart = Cart(user_id=user_id)
            session.add(cart)
            session.flush()

            for item in quote.items:
                if item.response_price is None:
                    raise ValueError(f"Cannot accept quote; item '{item.product.name}' has not been priced by an admin.")
                
                # Create a cart item with the custom price from the quote
                cart_item = CartItem(
                    cart_id=cart.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.response_price  # Using the custom price
                )
                session.add(cart_item)

            quote.status = 'accepted'
            session.commit()
            self.logger.info(f"Quote {quote_id} accepted by user {user_id}. New cart {cart.id} created with custom pricing.")
            return cart

        except (SQLAlchemyError, ValueError) as e:
            session.rollback()
            self.logger.error(f"Error accepting quote {quote_id}: {e}")
            raise

    
            
    def get_quote_by_id(self, quote_id):
        return session.query(Quote).options(
            joinedload(Quote.items).joinedload(QuoteItem.product),
            joinedload(Quote.user)
        ).filter_by(id=quote_id).first()
    
    @staticmethod
    def update_quote(quote_id, data):
        """Update a quote"""
        try:
            quote_id = InputSanitizer.InputSanitizer.sanitize_input(quote_id)
            
            quote = Quote.query.get(quote_id)
            if not quote:
                raise NotFoundException("Quote not found")
            
            # Update fields
            if 'total_amount' in data:
                quote.total_amount = float(InputSanitizer.InputSanitizer.sanitize_input(data['total_amount']))
            if 'notes' in data:
                quote.notes = InputSanitizer.InputSanitizer.sanitize_input(data['notes'])
            if 'status' in data:
                quote.status = InputSanitizer.InputSanitizer.sanitize_input(data['status'])
            
            quote.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # Log the action
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
            quote_id = InputSanitizer.InputSanitizer.sanitize_input(quote_id)
            
            quote = Quote.query.get(quote_id)
            if not quote:
                return False
            
            # Check if quote has been converted to invoice
            if hasattr(quote, 'invoice') and quote.invoice:
                raise ValidationException("Cannot delete quote that has been converted to invoice")
            
            db.session.delete(quote)
            db.session.commit()
            
            # Log the action
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
            quote_id = InputSanitizer.InputSanitizer.sanitize_input(quote_id)
            
            quote = Quote.query.get(quote_id)
            if not quote:
                raise NotFoundException("Quote not found")
            
            if quote.status != 'pending':
                raise ValidationException("Quote is not in pending status")
            
            quote.status = 'approved'
            quote.approved_at = datetime.utcnow()
            
            db.session.commit()
            
            # Log the action
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
            quote_id = InputSanitizer.InputSanitizer.sanitize_input(quote_id)
            reason = InputSanitizer.InputSanitizer.sanitize_input(reason) if reason else None
            
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
            
            # Log the action
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
            b2b_account_id = InputSanitizer.InputSanitizer.sanitize_input(b2b_account_id)
            
            quotes = Quote.query.filter_by(b2b_account_id=b2b_account_id)\
                              .order_by(Quote.created_at.desc()).all()
            return quotes
            
        except Exception as e:
            MonitoringService.log_error(f"Error getting quotes for account {b2b_account_id}: {str(e)}")
            raise ServiceError(f"Failed to get quotes: {str(e)}")
