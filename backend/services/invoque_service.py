
from backend.models.order_models import Invoice, Order
from backend.database import db
from backend.services.exceptions import NotFoundException
from sqlalchemy import desc

class InvoiceService:
    @staticmethod
    def get_invoices_for_user(user_id):
        """Get all invoices for a specific user."""
        return db.session.query(Invoice).join(Order)\
            .filter(Order.user_id == user_id)\
            .order_by(desc(Invoice.created_at))\
            .all()
    
    @staticmethod
    def get_invoice_by_id(invoice_id, user_id=None):
        """Get a specific invoice, optionally filtered by user."""
        query = db.session.query(Invoice).join(Order)\
            .filter(Invoice.id == invoice_id)
        if user_id:
            query = query.filter(Order.user_id == user_id)
        return query.first()
    
    @staticmethod
    def generate_invoice_pdf(invoice_id, user_id):
        """Generate or retrieve the PDF path for an invoice."""
        invoice = InvoiceService.get_invoice_by_id(invoice_id, user_id)
        if not invoice:
            raise NotFoundException("Invoice not found")
        
        # If PDF already exists, return path
        if invoice.pdf_path:
            return invoice.pdf_path
        
        # Generate PDF logic would go here
        # For now, return a placeholder
        return f"/invoices/invoice_{invoice_id}.pdf"
    
    @staticmethod
    def create_invoice_for_order(order_id):
        """Create an invoice for a completed order."""
        order = Order.query.get(order_id)
        if not order:
            raise NotFoundException("Order not found")
        
        # Check if invoice already exists
        existing_invoice = Invoice.query.filter_by(order_id=order_id).first()
        if existing_invoice:
            return existing_invoice
        
        # Generate invoice number
        invoice_count = Invoice.query.count() + 1
        invoice_number = f"INV-{invoice_count:06d}"
        
        invoice = Invoice(
            order_id=order_id,
            invoice_number=invoice_number
        )
        
        db.session.add(invoice)
        db.session.commit()
        return invoice
