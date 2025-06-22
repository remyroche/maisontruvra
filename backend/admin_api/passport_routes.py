from flask import Blueprint, jsonify
from backend.services.passport_service import PassportService
from backend.auth.permissions import admin_required

passport_routes = Blueprint('admin_passport_routes', __name__)

@passport_routes.route('/passports', methods=['GET'])
@admin_required
def get_all_passports():
    passports = PassportService.get_all_passports()
    return jsonify([p.to_dict() for p in passports]), 200

@passport_routes.route('/passports/<string:passport_id>', methods=['GET'])
@admin_required
def get_passport_details(passport_id):
    passport = PassportService.get_passport_by_id(passport_id)
    if passport:
        return jsonify(passport.to_dict_detailed()), 200
    return jsonify({"error": "Passport not found"}), 404
