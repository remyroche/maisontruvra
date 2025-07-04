# backend/services/invoice_service.py

from .. import db
from ..models import Order, Invoice
from .exceptions import NotFoundException, ServiceException

# FIX: Import the PDFService class, not a function
from .pdf_service import PDFService

import logging

logger = logging.getLogger(__name__)


class InvoiceService:
    """
    Handles all logic related to creating and managing invoices.
    """

    def __init__(self, session=None):
        self.session = session or db.session
        # FIX: Create an instance of the PDFService
        self.pdf_service = PDFService()

    def generate_invoice_for_order(self, order_id):
        """
        Generates a PDF invoice for a given order and saves it.
        This method is designed to be called asynchronously by a Celery task.
        """
        order = self.session.query(Order).get(order_id)
        if not order:
            raise NotFoundException(resource_name="Order", resource_id=order_id)

        try:
            # FIX: Call the method on the PDFService instance
            pdf_path = self.pdf_service.create_invoice_pdf(order)

            # Create a new invoice record in the database
            new_invoice = Invoice(
                order_id=order.id,
                invoice_number=f"INV-{order.id[:8]}",  # Example invoice number
                pdf_url=pdf_path,  # Assuming this path is a URL or retrievable path
            )
            self.session.add(new_invoice)
            self.session.commit()

            logger.info(
                f"Successfully generated and saved invoice for order {order_id} at {pdf_path}"
            )
            return new_invoice

        except Exception as e:
            self.session.rollback()
            logger.error(
                f"Failed to generate invoice for order {order_id}: {e}", exc_info=True
            )
            raise ServiceException("Failed to generate invoice.")
