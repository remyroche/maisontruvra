from flask import Blueprint, jsonify
from backend.services.passport_service import PassportService
from backend.utils.input_sanitizer import InputSanitizer

passport_bp = Blueprint("passport_bp", __name__, url_prefix="/api/passport")


# READ a product passport by its unique token ID (public access)
@passport_bp.route("/<string:token_id>", methods=["GET"])
def get_public_passport(token_id):
    """
    Get public information for a product passport by its unique token ID.
    This endpoint is publicly accessible.
    """
    clean_token_id = InputSanitizer.sanitize_input(token_id)
    try:
        passport = PassportService.get_passport_by_token_id(clean_token_id)
        if not passport:
            return jsonify(status="error", message="Product passport not found."), 404

        # Use a serializer that only exposes public-safe information
        return jsonify(status="success", data=passport.to_dict_for_public()), 200
    except Exception:
        # Log error e
        return jsonify(
            status="error",
            message="An error occurred while fetching the product passport.",
        ), 500
