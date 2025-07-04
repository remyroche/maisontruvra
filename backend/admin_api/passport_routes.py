import io

from flask import Blueprint, jsonify, send_file

from backend.services.passport_service import (
    PassportService,
)  # Assuming this service exists
from backend.utils.decorators import (
    permissions_required,
    roles_required,
)

passport_bp = Blueprint(
    "admin_passport_routes", __name__, url_prefix="/api/admin/passports"
)


@passport_bp.route("/", methods=["GET"])
@permissions_required("MANAGE_PASSPORTS")
@roles_required("Admin", "Staff")
def get_passports():
    """Retrieves all generated product passports."""
    passports = PassportService.get_all_passports()
    return jsonify([p.to_dict() for p in passports])


@passport_bp.route("/<int:passport_id>/download", methods=["GET"])
@permissions_required("MANAGE_PASSPORTS")
@roles_required("Admin", "Staff")
def download_passport(passport_id):
    """Generates and serves a PDF for a specific product passport."""
    try:
        pdf_buffer = PassportService.generate_passport_pdf(passport_id)
        if not pdf_buffer:
            return jsonify({"error": "Passport not found"}), 404

        return send_file(
            io.BytesIO(pdf_buffer),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"product_passport_{passport_id}.pdf",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
