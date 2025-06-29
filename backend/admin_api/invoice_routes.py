from flask import Blueprint, request, jsonify
from backend.database import db
from backend.models.invoice_models import Quote, Invoice
from backend.services.invoice_service import InvoiceService
from backend.utils.decorators import staff_required, roles_required, permissions_required

admin_invoice_bp = Blueprint('admin_invoice_bp', __name__, url_prefix='/api/admin')
invoice_service = InvoiceService(db.session)

@admin_invoice_bp.route('/quotes', methods=['GET'])
@roles_required ('Admin', 'Manager', 'Support')
def get_all_quotes():
    quotes = Quote.query.filter_by(status='pending').order_by(Quote.created_at.desc()).all()
    quote_list = [{
        'id': q.id, 'b2b_account_id': q.b2b_account_id, 'company_name': q.b2b_account.company_name,
        'user_request': q.user_request, 'created_at': q.created_at.isoformat()
    } for q in quotes]
    return jsonify(quote_list)

@admin_invoice_bp.route('/quotes/<int:quote_id>/convert-to-invoice', methods=['POST'])
@roles_required ('Admin', 'Manager', 'Support')
def convert_to_invoice(quote_id):
    data = request.get_json()
    items = data.get('items')
    due_date = data.get('due_date')

    if not items:
        return jsonify({"error": "Invoice must have at least one item."}), 400
        
    try:
        invoice = invoice_service.convert_quote_to_invoice(quote_id, items, due_date)
        # Transition status to pending signature so user can sign it
        invoice_service.update_invoice_status(invoice.id, 'pending_signature')
        return jsonify({"message": "Invoice created successfully.", "invoice_id": invoice.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
        
@admin_invoice_bp.route('/invoices/<int:invoice_id>/status', methods=['PUT'])
@roles_required ('Admin', 'Manager', 'Support')
def update_invoice_status(invoice_id):
    data = request.get_json()
    new_status = data.get('status')
    
    try:
        invoice_service.update_invoice_status(invoice_id, new_status)
        return jsonify({"message": f"Invoice status updated to {new_status}."}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
