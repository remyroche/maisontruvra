
from backend.models.order_models import Invoice, Order
from backend.database import db
from backend.services.exceptions import NotFoundException
from sqlalchemy import desc
import os
from datetime import datetime
from flask import render_template, current_app
from weasyprint import HTML
from backend.database import db
from backend.models.invoice_models import Invoice  # A new model you'll need to create
from backend.services.email_service import EmailService # Assumed email service

class B2BInvoiceService:
    @staticmethod
    def _generate_b2b_invoice_number() -> str:
        """Generates a unique invoice number, e.g., INV-YYYYMM-XXXX."""
        today = datetime.utcnow()
        # Find the last invoice for this month to increment the number
        last_invoice = Invoice.query.filter(
            db.func.strftime('%Y-%m', Invoice.created_at) == today.strftime('%Y-%m')
        ).order_by(Invoice.id.desc()).first()
        
        count = 1
        if last_invoice and last_invoice.invoice_number:
            try:
                count = int(last_invoice.invoice_number.split('-')[-1]) + 1
            except (ValueError, IndexError):
                pass # Fallback to 1 if parsing fails
                
        return f"INV-{today.strftime('%Y%m')}-{count:04d}"

    @staticmethod
    def create_and_send_b2b_invoice(order: Order):
        """
        Main function to generate, save, and send a B2B invoice.
        This should be called by the OrderService after an order is confirmed.
        """
        if not order:
            raise ValueError("Une commande est requise pour générer une facture.")

        # 1. Prepare the data for the template
        context = {
            "invoice": {
                "number": InvoiceService._generate_invoice_number(),
                "issue_date": datetime.utcnow().strftime('%d/%m/%Y'),
            },
            "client": order.user.company_profile, # Assuming a relationship
            "order": order,
            "totals": order.calculate_totals(), # Assuming an order method to calculate totals
            "company": { # This should come from your app's global config
                "legal_status": "SAS",
                "siret": "123 456 789 00010",
                "capital": "10,000",
                "address": "14 rue de la Libération, 93330 Neuilly-sur-Marne",
                "vat_number": "FRXX123456789",
                "email": "contact@maisontruvra.com",
                "bic": "AGRIFRPPXXX",
                "iban": "FR76 ...",
            }
        }

        # 2. Render the HTML template
        html_out = render_template('b2b_invoice.html', **context)

        # 3. Generate the PDF from the rendered HTML
        pdf_bytes = HTML(string=html_out).write_pdf()

        # 4. Save the invoice to the database and storage
        # The filename could be stored in a cloud bucket like S3 or locally.
        pdf_filename = f"facture-{context['invoice']['number']}.pdf"
        
        # Example of saving locally (for production, use a cloud service)
        storage_path = os.path.join(current_app.config.get("INVOICE_STORAGE_PATH"), pdf_filename)
        with open(storage_path, 'wb') as f:
            f.write(pdf_bytes)

        new_invoice = Invoice(
            invoice_number=context['invoice']['number'],
            user_id=order.user_id,
            order_id=order.id,
            file_path=storage_path, # Store the path to the PDF
            total_amount=context['totals']['net_total']
        )
        db.session.add(new_invoice)
        
        # 5. Send the confirmation email with the invoice attached
        EmailService.send_order_confirmation(
            recipient=order.user.email,
            order=order,
            invoice_attachment={
                "data": pdf_bytes,
                "filename": pdf_filename,
                "mimetype": "application/pdf"
            }
        )

        # The calling service should handle the final db.session.commit()
        return new_invoice



class B2CInvoiceService:
    @staticmethod
    def get_B2Cinvoices_for_user(user_id):
        """Get all invoices for a specific user."""
        return db.session.query(Invoice).join(Order)\
            .filter(Order.user_id == user_id)\
            .order_by(desc(Invoice.created_at))\
            .all()
    
    @staticmethod
    def get_B2Cinvoice_by_id(invoice_id, user_id=None):
        """Get a specific invoice, optionally filtered by user."""
        query = db.session.query(Invoice).join(Order)\
            .filter(Invoice.id == invoice_id)
        if user_id:
            query = query.filter(Order.user_id == user_id)
        return query.first()
    
    @staticmethod
    def generate_B2Cinvoice_pdf(invoice_id, user_id):
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
    def create_B2Cinvoice_for_order(order_id):
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
