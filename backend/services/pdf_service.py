# backend/services/pdf_service.py
# This is a new service dedicated to PDF generation.

from playwright.sync_api import sync_playwright
from flask import render_template, current_app
from backend.services.monitoring_service import MonitoringService
import os
from datetime import datetime

class PDFService:
    def __init__(self, logger):
        self.logger = logger
        
    """
    Handles the generation of PDF documents from HTML templates.
    """
    def generate_invoice(self, order):
        """
        Generates a PDF invoice for a given order using Playwright.
        """
        try:
            self.logger.info(f"Generating invoice for order {order.id} using Playwright.")
            # Determine template based on user type (B2C vs B2B)
            template_name = 'non-email/b2b_invoice.html' if order.user.is_b2b else 'non-email/b2c_invoice.html'
            
            html_string = render_template(template_name, order=order)
            
            pdf_folder = current_app.config.get('INVOICE_PDF_FOLDER', 'invoices')
            if not os.path.exists(pdf_folder):
                os.makedirs(pdf_folder)

            file_name = f"invoice_{order.id}_{datetime.utcnow().timestamp()}.pdf"
            file_path = os.path.join(pdf_folder, file_name)

            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.set_content(html_string)
                page.pdf(path=file_path, format='A4', print_background=True)
                browser.close()
            
            self.logger.info(f"Successfully generated invoice: {file_path}")
            return file_path
        except Exception as e:
            self.logger.error(f"Failed to generate invoice for order {order.id}: {e}")
            return None

    def generate_passport_pdf(self, passport_data):
        """
        Generates a PDF for a product passport using Playwright.
        """
        try:
            product_name = passport_data.get('product_name', 'Unknown Product')
            self.logger.info(f"Generating passport PDF for product: {product_name} using Playwright.")
            
            template_name = 'non-email/product_passport.html'
            html_string = render_template(template_name, passport=passport_data)
            
            pdf_folder = current_app.config.get('PASSPORT_PDF_FOLDER', 'passports')
            if not os.path.exists(pdf_folder):
                os.makedirs(pdf_folder)

            sku = passport_data.get('product_sku', 'unknown_sku')
            file_name = f"passport_{sku}_{int(datetime.utcnow().timestamp())}.pdf"
            file_path = os.path.join(pdf_folder, file_name)

            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.set_content(html_string)
                page.pdf(path=file_path, format='A4', print_background=True)
                browser.close()

            self.logger.info(f"Successfully generated passport PDF: {file_path}")
            return file_path
        except Exception as e:
            self.logger.error(f"Failed to generate passport PDF for '{product_name}': {e}")
            return None

