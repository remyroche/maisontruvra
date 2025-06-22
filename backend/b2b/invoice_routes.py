from flask import Blueprint, jsonify, send_file
from backend.auth.permissions import b2b_user_required
from flask_jwt_extended import get_jwt_identity
from backend.services.invoice_service import InvoiceService
from backend.services.exceptions import NotFoundException

invoice_routes = Blueprint('b2b_invoice_routes', __name__)

@invoice_routes.route('/invoices', methods=['GET'])
@b2b_user_required
def get_b2b_invoices():
    """
    Get a list of all invoices for the B2B user.
    """
    user_id = get_jwt_identity()
    invoices = InvoiceService.get_invoices_for_user(user_id)
    return jsonify([inv.to_dict() for inv in invoices]), 200

@invoice_routes.route('/invoices/<int:invoice_id>/download', methods=['GET'])
@b2b_user_required
def download_b2b_invoice(invoice_id):
    """
    Download a specific invoice PDF.
    """
    user_id = get_jwt_identity()
    try:
        # The service should verify that the invoice belongs to the user
        pdf_path = InvoiceService.generate_invoice_pdf(invoice_id, user_id)
        return send_file(pdf_path, as_attachment=True)
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Could not generate invoice PDF."}), 500