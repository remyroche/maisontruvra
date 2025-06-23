from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.b2b_service import B2BService
from backend.auth.permissions import b2b_user_required

b2b_invoice_bp = Blueprint('b2b_invoice_bp', __name__, url_prefix='/api/b2b/invoices')

# GET a list of invoices for the current B2B user
@b2b_invoice_bp.route('/', methods=['GET'])
@b2b_user_required
def get_invoices():
    """
    Get a paginated list of invoices for the currently authenticated B2B user.
    """
    user_id = get_jwt_identity()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
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

# GET a single invoice by ID
@b2b_invoice_bp.route('/<int:invoice_id>', methods=['GET'])
@b2b_user_required
def get_invoice(invoice_id):
    """
    Get a single invoice by its ID.
    Ensures the invoice belongs to the currently authenticated B2B user.
    """
    user_id = get_jwt_identity()
    try:
        invoice = B2BService.get_invoice_by_id_for_user(invoice_id, user_id)
        if invoice:
            return jsonify(status="success", data=invoice.to_dict_with_details()), 200
        return jsonify(status="error", message="Invoice not found or you do not have permission to view it."), 404
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal error occurred."), 500

