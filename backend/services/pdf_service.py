# backend/services/pdf_service.py
# This is a new service dedicated to PDF generation.

from playwright.sync_api import sync_playwright
from flask import render_template, current_app

class PDFService:
    """
    Handles the generation of PDF documents from HTML templates.
    """
    def generate_invoice_pdf(self, order):
        """
        Renders an invoice HTML template for an order and converts it to a PDF.

        Args:
            order (Order): The SQLAlchemy Order object.

        Returns:
            bytes: The generated PDF content as bytes.
        """
        # Determine the correct template based on user type
        template_name = (
            'non-email/b2b_invoice.html' if order.user_type == 'b2b' 
            else 'non-email/b2c_invoice.html'
        )

        try:
            # We must be in an application context to use render_template
            with current_app.app_context():
                html_content = render_template(template_name, order=order)
        except Exception as e:
            current_app.logger.error(f"Error rendering invoice template for order {order.id}: {e}")
            raise

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.set_content(html_content, wait_until='networkidle')
                pdf_bytes = page.pdf(format='A4', print_background=True)
                browser.close()
                return pdf_bytes
        except Exception as e:
            current_app.logger.error(f"Error generating PDF with Playwright for order {order.id}: {e}")
            raise

