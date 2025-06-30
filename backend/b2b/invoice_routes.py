from flask import Blueprint, jsonify, request, session, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.b2b_service import B2BService
from backend.services.invoice_service import InvoiceService # Assuming this service exists
from backend.utils.decorators import staff_required, b2b_user_required, roles_required, permissions_required, api_resource_handler
import io
from io import BytesIO
from backend.utils.input_sanitizer import InputSanitizer
from backend.database import db
from backend.models.b2b_models import B2BUser
from backend.models.invoice_models import Quote, Invoice
from backend.services.invoice_service import InvoiceService
from backend.schemas import QuoteRequestSchema, InvoiceSignatureSchema

b2b_invoice_bp = Blueprint('b2b_invoice_bp', __name__, url_prefix='/api/b2b')
# InvoiceService uses static methods, no instantiation needed
invoice_bp = Blueprint('admin_invoice_routes', __name__, url_prefix='/api/admin/invoices')

# GET a list of invoices for the current B2B user
@invoice_bp.route('/', methods=['GET'])
@b2b_user_required
@roles_required ('Admin', 'Manager', 'Support')
def get_invoices():
    """
    Get a paginated list of invoices for the currently authenticated B2B user.
    """
    user_id = get_jwt_identity()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = InputSanitizer.InputSanitizer.sanitize_input(request.args.get('status'))
        
        invoices_pagination = B2BService.get_user_invoices_paginated(user_id, page=page, per_page=per_page)
        
        return jsonify({
            "status": "success",
            "data": [invoice.to_dict() for invoice in invoices_pagination.items],
            "total": invoices_pagination.total,
            "pages": invoices_pagination.pages,
            "current_page": invoices_pagination.page
        }), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal error occurred while fetching invoices."), 500

@b2b_invoice_bp.route('/quotes', methods=['POST'])
@api_resource_handler(Quote, schema=QuoteRequestSchema())
@b2b_user_required
def submit_quote_request():
    b2b_user_id = session.get('b2b_user_id')
    current_user = db.session.get(B2BUser, b2b_user_id)
    
    try:
        quote = InvoiceService.create_quote(
            b2b_account_id=current_user.account_id,
            user_request=g.validated_data['request_details']
        )
        return jsonify({"message": "Quote request submitted successfully.", "quote_id": quote.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@b2b_invoice_bp.route('/invoices/<int:invoice_id>/sign', methods=['POST'])
@api_resource_handler(Invoice, schema=InvoiceSignatureSchema(), check_ownership=True)
@b2b_user_required
def sign_invoice(invoice_id):
    b2b_user_id = session.get('b2b_user_id')
    current_user = db.session.get(B2BUser, b2b_user_id)
    
    # Invoice is already validated and available as g.invoice
    invoice = g.invoice

    if invoice.b2b_account_id != current_user.account_id:
        return jsonify({"error": "Invoice not found."}), 404
        
    try:
        InvoiceService.sign_invoice(invoice_id, g.validated_data['signature_data'])
        return jsonify({"message": "Invoice signed successfully."}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# GET a single invoice by ID
@b2b_invoice_bp.route('/<int:invoice_id>', methods=['GET'])
@api_resource_handler(Invoice, check_ownership=True)
@b2b_user_required
@roles_required ('Admin', 'Manager', 'Support')
def get_invoice(invoice_id):
    """
    Get a single invoice by its ID.
    Ensures the invoice belongs to the currently authenticated B2B user.
    """
    try:
        # Invoice is already validated and available as g.invoice
        invoice = g.invoice
        return jsonify(status="success", data=invoice.to_dict_with_details()), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal error occurred."), 500

