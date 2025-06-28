from backend.database import db
from backend.models.invoice_models import Quote, Invoice
from backend.models.b2b_models import B2BAccount
from backend.services.exceptions import NotFoundException, ValidationException, ServiceError
from backend.utils.sanitization import sanitize_input
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
            current_app.logger.error(f"Error getting all quotes: {str(e)}")
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
            current_app.logger.error(f"Error getting paginated quotes: {str(e)}")
            raise ServiceError(f"Failed to get quotes: {str(e)}")
    
    @staticmethod
    def get_quote_by_id(quote_id):
        """Get a quote by ID"""
        try:
            quote_id = sanitize_input(quote_id)
            quote = Quote.query.get(quote_id)
            if not quote:
                raise NotFoundException("Quote not found")
            return quote
        except Exception as e:
            current_app.logger.error(f"Error getting quote {quote_id}: {str(e)}")
            raise ServiceError(f"Failed to get quote: {str(e)}")
    
    @staticmethod
    def create_quote(b2b_account_id, items, notes=None):
        """Create a new quote"""
        try:
            b2b_account_id = sanitize_input(b2b_account_id)
            notes = sanitize_input(notes) if notes else None
            
            # Verify B2B account exists
            account = B2BAccount.query.get(b2b_account_id)
            if not account:
                raise NotFoundException("B2B account not found")
            
            # Calculate total amount
            total_amount = 0
            for item in items:
                quantity = int(sanitize_input(item.get('quantity', 0)))
                unit_price = float(sanitize_input(item.get('unit_price', 0)))
                total_amount += quantity * unit_price
            
            # Create quote
            quote = Quote(
                b2b_account_id=b2b_account_id,
                total_amount=total_amount,
                notes=notes,
                status='pending',
                created_at=datetime.utcnow()
            )
            
            db.session.add(quote)
            db.session.commit()
            
            # Log the action
            AuditLogService.log_action(
                user_id=None,  # System action
                action="CREATE_QUOTE",
                resource_type="QUOTE",
                resource_id=quote.id,
                details=f"Created quote for B2B account {b2b_account_id}"
            )
            
            current_app.logger.info(f"Created quote {quote.id} for B2B account {b2b_account_id}")
            return quote
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating quote: {str(e)}")
            raise ServiceError(f"Failed to create quote: {str(e)}")
    
    @staticmethod
    def update_quote(quote_id, data):
        """Update a quote"""
        try:
            quote_id = sanitize_input(quote_id)
            
            quote = Quote.query.get(quote_id)
            if not quote:
                raise NotFoundException("Quote not found")
            
            # Update fields
            if 'total_amount' in data:
                quote.total_amount = float(sanitize_input(data['total_amount']))
            if 'notes' in data:
                quote.notes = sanitize_input(data['notes'])
            if 'status' in data:
                quote.status = sanitize_input(data['status'])
            
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
            
            current_app.logger.info(f"Updated quote {quote_id}")
            return quote
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating quote {quote_id}: {str(e)}")
            raise ServiceError(f"Failed to update quote: {str(e)}")
    
    @staticmethod
    def delete_quote(quote_id):
        """Delete a quote"""
        try:
            quote_id = sanitize_input(quote_id)
            
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
            
            current_app.logger.info(f"Deleted quote {quote_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting quote {quote_id}: {str(e)}")
            raise ServiceError(f"Failed to delete quote: {str(e)}")
    
    @staticmethod
    def approve_quote(quote_id):
        """Approve a quote"""
        try:
            quote_id = sanitize_input(quote_id)
            
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
            
            current_app.logger.info(f"Approved quote {quote_id}")
            return quote
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error approving quote {quote_id}: {str(e)}")
            raise ServiceError(f"Failed to approve quote: {str(e)}")
    
    @staticmethod
    def reject_quote(quote_id, reason=None):
        """Reject a quote"""
        try:
            quote_id = sanitize_input(quote_id)
            reason = sanitize_input(reason) if reason else None
            
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
            
            current_app.logger.info(f"Rejected quote {quote_id}")
            return quote
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error rejecting quote {quote_id}: {str(e)}")
            raise ServiceError(f"Failed to reject quote: {str(e)}")
    
    @staticmethod
    def get_quotes_by_account(b2b_account_id):
        """Get all quotes for a B2B account"""
        try:
            b2b_account_id = sanitize_input(b2b_account_id)
            
            quotes = Quote.query.filter_by(b2b_account_id=b2b_account_id)\
                              .order_by(Quote.created_at.desc()).all()
            return quotes
            
        except Exception as e:
            current_app.logger.error(f"Error getting quotes for account {b2b_account_id}: {str(e)}")
            raise ServiceError(f"Failed to get quotes: {str(e)}")