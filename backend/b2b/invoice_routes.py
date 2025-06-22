from flask import Blueprint, jsonify, send_file, redirect
from backend.auth.permissions import b2b_user_required
from flask_jwt_extended import get_jwt_identity
from backend.services.invoice_service import InvoiceService
from backend.services.exceptions import NotFoundException
from backend.auth.permissions import b2b_user_required

invoice_routes = Blueprint('b2b_invoice_routes', __name__)

@b2b_bp.route('/invoices', methods=['GET'])
@b2b_user_required
def list_invoices():
    """
    Returns a list of all available invoices for the logged-in B2B user.
    """
    user_id = get_jwt_identity()
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, order_id, invoice_number, generated_at
            FROM invoices
            WHERE user_id = %s AND deleted_at IS NULL
            ORDER BY generated_at DESC
            """,
            (user_id,)
        )
        invoices = cursor.fetchall()
        return jsonify(invoices), 200
    except Exception as e:
        logger.error(f"Failed to list invoices for user {user_id}: {e}")
        return jsonify({"error": "An internal error occurred."}), 500
    finally:
        cursor.close()
        conn.close()

@b2b_bp.route('/invoices/<int:invoice_id>/download', methods=['GET'])
@b2b_user_required
def download_invoice(invoice_id):
    """
    Provides a secure, temporary link to download a specific invoice PDF.
    It generates a pre-signed URL to the private file in storage.
    """
    user_id = get_jwt_identity()
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Verify the user owns this invoice before proceeding.
        cursor.execute(
            "SELECT file_path FROM invoices WHERE id = %s AND user_id = %s",
            (invoice_id, user_id)
        )
        invoice = cursor.fetchone()
        if not invoice:
            return jsonify({"error": "Invoice not found or access denied."}), 404

        # 2. Generate a temporary, secure URL to the file in storage (e.g., S3 pre-signed URL).
        # This prevents direct, public access to the invoice files.
        download_url = storage_service.generate_presigned_url(invoice['file_path'])
        
        # 3. Redirect the user's browser to the pre-signed URL to initiate the download.
        return redirect(download_url, code=302)

    except Exception as e:
        logger.error(f"Failed to generate download link for invoice {invoice_id}: {e}")
        return jsonify({"error": "An internal error occurred."}), 500
    finally:
        cursor.close()
        conn.close()
        
