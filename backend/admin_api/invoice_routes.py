from flask import Blueprint, g, jsonify

from backend.database import db
from backend.services.exceptions import ValidationException
from backend.utils.decorators import (
    api_resource_handler,
    roles_required,
)

admin_invoice_bp = Blueprint("admin_invoice_bp", __name__, url_prefix="/api/admin")
invoice_service = InvoiceService(db.session)
order_routes = Blueprint("order_routes", __name__, url_prefix="/b2b/orders")


@admin_invoice_bp.route("/quotes", methods=["GET"])
@roles_required("Admin", "Manager", "Support")
def get_all_quotes():
    quotes = (
        Quote.query.filter_by(status="pending").order_by(Quote.created_at.desc()).all()
    )
    quote_list = [
        {
            "id": q.id,
            "b2b_account_id": q.b2b_account_id,
            "company_name": q.b2b_account.company_name,
            "user_request": q.user_request,
            "created_at": q.created_at.isoformat(),
        }
        for q in quotes
    ]
    return jsonify(quote_list)


@admin_invoice_bp.route("/quotes/<int:quote_id>/convert-to-invoice", methods=["POST"])
@api_resource_handler(
    model=Quote,
    request_schema=InvoiceSchema,  # Schema for invoice creation data
    response_schema=InvoiceSchema,  # Return the created invoice
    ownership_exempt_roles=[
        "Admin",
        "Manager",
        "Support",
    ],  # Staff can convert any quote
    cache_timeout=0,  # No caching for invoice creation
    log_action=True,  # Log invoice creation
)
@roles_required("Admin", "Manager", "Support")
def convert_to_invoice(quote_id):
    """
    Convert a quote to an invoice.
    """
    # Quote is already fetched and validated by decorator

    # Get validated invoice data
    invoice_data = g.validated_data
    items = invoice_data.get("items")
    due_date = invoice_data.get("due_date")

    if not items:
        raise ValidationException("Invoice must have at least one item.")

    try:
        invoice = invoice_service.convert_quote_to_invoice(quote_id, items, due_date)
        # Transition status to pending signature so user can sign it
        invoice_service.update_invoice_status(invoice.id, "pending_signature")
        return invoice
    except ValueError as e:
        raise ValidationException(str(e)) from e


@admin_invoice_bp.route("/invoices/<int:invoice_id>/status", methods=["PUT"])
@api_resource_handler(
    model=Invoice,
    request_schema=InvoiceStatusUpdateSchema,
    response_schema=InvoiceSchema,
    ownership_exempt_roles=[
        "Admin",
        "Manager",
        "Support",
    ],  # Staff can update any invoice
    cache_timeout=0,  # No caching for status updates
    log_action=True,  # Log status changes
)
@roles_required("Admin", "Manager", "Support")
def update_invoice_status(invoice_id):
    """
    Update the status of an invoice.
    """
    # Invoice is already fetched and validated by decorator
    invoice = g.target_object

    # Get validated status data
    new_status = g.validated_data.get("status")

    try:
        updated_invoice = invoice_service.update_invoice_status(invoice_id, new_status)
        return updated_invoice or invoice
    except ValueError as e:
        raise ValidationException(str(e)) from e
