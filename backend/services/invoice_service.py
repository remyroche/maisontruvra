import os
from datetime import datetime
from flask import render_template, current_app
from weasyprint import HTML

from backend.database import db
from backend.models.order_models import Order
from backend.models.invoice_models import Invoice # Create this new model
from backend.services.email_service import EmailService # Create this new service

class InvoiceService:
    """
    A unified service to handle invoice generation for both B2B and B2C orders.
    """

    @staticmethod
    def _generate_invoice_number(prefix: str = "INV") -> str:
        """Generates a unique invoice number with a given prefix (e.g., INV or RCT)."""
        today = datetime.utcnow()
        last_invoice = Invoice.query.filter(
            db.func.strftime('%Y-%m', Invoice.created_at) == today.strftime('%Y-%m')
        ).order_by(Invoice.id.desc()).first()
        
        count = 1
        if last_invoice and last_invoice.invoice_number:
            try:
                count = int(last_invoice.invoice_number.split('-')[-1]) + 1
            except (ValueError, IndexError):
                pass
                
        return f"{prefix}-{today.strftime('%Y%m')}-{count:04d}"

    @staticmethod
    def _render_invoice_html(order: Order) -> str:
        """Renders the correct HTML template based on the user type."""
        user = order.user
        
        # Prepare the context data for the template
        context = {
            "order": order,
            "totals": order.calculate_totals(), # Assumes method exists on Order model
            "company": {
                "legal_status": "SAS", "siret": "123 456 789 00010",
                "capital": "10,000", "address": "14 rue de la Libération, 93330 Neuilly-sur-Marne",
                "vat_number": "FRXX123456789", "email": "contact@maisontruvra.com",
                "bic": "AGRIFRPPXXX", "iban": "FR76 ...",
            }
        }

        if user and user.user_type == 'B2B':
            context["invoice"] = {
                "number": InvoiceService._generate_invoice_number("INV"),
                "issue_date": datetime.utcnow().strftime('%d/%m/%Y'),
                "type_name": "Facture"
            }
            context["client"] = user.company_profile # Assumes relationship exists
            return render_template('invoices/b2b_invoice.html', **context), context["invoice"]["number"]
        else: # Default to B2C
            context["receipt"] = {
                "number": InvoiceService._generate_invoice_number("RECU"),
                "issue_date": datetime.utcnow().strftime('%d/%m/%Y'),
                "type_name": "Reçu"
            }
            context["client"] = user
            # You would create a simpler 'b2c_receipt.html' template for this
            return render_template('invoices/b2c_receipt.html', **context), context["receipt"]["number"]

    @staticmethod
    def create_invoice_for_order(order: Order):
        """
        Main function to generate, save, and email an invoice/receipt for an order.
        """
        if not order:
            raise ValueError("Une commande est requise pour générer une facture.")

        # 1. Render the correct HTML template (B2B Invoice or B2C Receipt)
        html_out, invoice_number = InvoiceService._render_invoice_html(order)

        # 2. Generate the PDF from the HTML
        pdf_bytes = HTML(string=html_out).write_pdf()
        pdf_filename = f"{invoice_number}.pdf"

        # 3. Save the PDF to a configured storage location
        storage_path = os.path.join(current_app.config.get("INVOICE_STORAGE_PATH"), pdf_filename)
        with open(storage_path, 'wb') as f:
            f.write(pdf_bytes)

        # 4. Create the Invoice record in the database
        new_invoice = Invoice(
            invoice_number=invoice_number,
            user_id=order.user_id,
            order_id=order.id,
            file_path=storage_path,
            total_amount=order.calculate_totals()['net_total']
        )
        db.session.add(new_invoice)
        
        # 5. Send the correct confirmation email with the invoice attached
        EmailService.send_order_confirmation(order, pdf_bytes, pdf_filename)

        # The calling service is responsible for the final db.session.commit()
        return new_invoice
