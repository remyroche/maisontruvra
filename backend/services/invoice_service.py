# backend/services/invoice_service.py
import os
from flask import current_app, render_template
from backend.database import db
from backend.models.order_models import Order
from backend.models.invoice_models import Invoice
from backend.models.order_models import Order, OrderStatus
from backend.services.pdf_service import create_invoice_pdf

def get_invoice_by_order_id(order_id):
    return Invoice.query.filter_by(order_id=order_id).first()

def get_invoice_by_b2b_order_id(b2b_order_id):
    return Invoice.query.filter_by(b2b_order_id=b2b_order_id).first()

def generate_invoice_pdf_for_order(order_id):
    """Generates a PDF invoice for a given order."""
    order = Order.query.get(order_id)
    if not order or order.status != OrderStatus.COMPLETED:
        current_app.logger.warning(
            f"Could not generate invoice for order {order_id}. Order not found or not completed."
        )
        return

    template_path = "non-email/b2c_invoice.html"
    invoice_html = render_template(template_path, order=order)
    invoice_pdf = create_invoice_pdf(invoice_html)

    invoice = Invoice(
        order_id=order_id,
        user_id=order.user_id,
        invoice_data=invoice_pdf,
    )
    db.session.add(invoice)
    db.session.commit()
    current_app.logger.info(f"Successfully generated invoice for order {order_id}")
    return invoice

def generate_invoice_pdf_for_b2b_order(order_id):
    """Generates a PDF invoice for a given B2B order."""
    order = Order.query.get(order_id)
    if not order:
        current_app.logger.warning(
            f"Could not generate invoice for B2B order {order_id}. Order not found."
        )
        return

    template_path = "non-email/b2b_invoice.html"
    invoice_html = render_template(template_path, order=order)
    invoice_pdf = create_invoice_pdf(invoice_html)

    invoice = Invoice(
        b2b_order_id=order_id,
        user_id=order.user_id,
        invoice_data=invoice_pdf,
    )
    db.session.add(invoice)
    db.session.commit()
    current_app.logger.info(f"Successfully generated invoice for B2B order {order_id}")
    return invoice
