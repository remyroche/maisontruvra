from flask import Blueprint, jsonify
from backend.services.passport_service import PassportService

passport_bp = Blueprint('passport_bp', __name__)

@passport_bp.route('/<string:passport_id>', methods=['GET'])
def get_passport(passport_id):
    """
    Get the details of a specific Product Passport.
    This is a public endpoint accessible via QR code scan.
    """
    passport = PassportService.get_passport_by_id(passport_id)
    if not passport:
        return jsonify({"error": "Product Passport not found."}), 404
    
    return jsonify(passport.to_dict_detailed()), 200
