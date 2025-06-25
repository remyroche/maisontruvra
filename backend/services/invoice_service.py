import os
from datetime import datetime
from flask import render_template, current_app
from weasyprint import HTML

from backend.database import db
from backend.models.order_models import Order
from backend.models.invoice_models import Invoice # Create this new model
from backend.tasks import generate_invoice_pdf_task
import logging
from backend.models.b2b_models import Invoice, B2BProfile

class InvoiceService:
    """
    A unified service to handle invoice generation for both B2B and B2C orders.
    """

class InvoiceService:
    @staticmethod
    def generate_pdf(order_id):
        """
        Generates a PDF for a given order by passing a full context
        dictionary to the relevant B2C or B2B template.
        """
        logger.info(f"Starting PDF generation for order_id: {order_id}")
        
        order = Order.query.options(db.joinedload(Order.user)).get(order_id)
        if not order:
            logger.error(f"Could not generate invoice: Order {order_id} not found.")
            raise ValueError(f"Order {order_id} not found")

        invoice = Invoice.query.filter_by(order_id=order.id).first()
        if not invoice:
            logger.error(f"Could not generate invoice: Invoice record for Order {order_id} not found.")
            raise ValueError(f"Invoice for Order {order_id} not found")

        # --- IMPLEMENTATION: Build a comprehensive context dictionary ---
        template_name = 'non-email/b2c_invoice.html'
        context = {
            'order': order,
            'invoice': invoice,
            'customer_name': f"{order.user.first_name} {order.user.last_name}",
            'billing_address': order.billing_address, # Assuming this relationship exists
            'shipping_address': order.shipping_address # Assuming this relationship exists
        }

        context['company'] = {
            'legal_status': current_app.config.get('COMPANY_LEGAL_STATUS', 'SAS'),
            'siret': current_app.config.get('COMPANY_SIRET', '123 456 789 00010'),
            'capital': current_app.config.get('COMPANY_CAPITAL', '10,000'),
            'address': current_app.config.get('COMPANY_ADDRESS', '123 Rue de la République, 75001 Paris, France'),
            'vat_number': current_app.config.get('COMPANY_VAT_NUMBER', 'FR00123456789'),
            'email': current_app.config.get('COMPANY_EMAIL', 'contact@maisontruvra.com')
        }

        # If the user is B2B, add B2B-specific details to the context
        if order.user.is_b2b:
            template_name = 'non-email/b2b_invoice.html'
            b2b_profile = B2BProfile.query.filter_by(user_id=order.user.id).first()
            if b2b_profile:
                context['company_name'] = b2b_profile.company_name
                context['vat_number'] = b2b_profile.vat_number

        try:
            # Render the correct template with the full context
            html_string = render_template(template_name, **context)
            
            # Use a library like WeasyPrint to convert the HTML to PDF
            pdf_file = HTML(string=html_string).write_pdf()
            
            # Save the PDF (e.g., to a cloud storage bucket)
            filename = f"invoices/invoice-{invoice.invoice_number}.pdf"
            # cloud_storage.save(pdf_file, filename) # Real implementation
            
            invoice.pdf_url = filename
            invoice.status = 'generated'
            db.session.commit()

            logger.info(f"PDF generation for invoice {invoice.invoice_number} completed. Saved to {filename}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"An error occurred during PDF generation for order {order_id}: {e}", exc_info=True)
            raise

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
        print(f"Invoice {new_invoice['id']} created. Queuing PDF generation.")
        generate_invoice_pdf_task.delay(order_id)

        # The calling service is responsible for the final db.session.commit()
        return new_invoice
