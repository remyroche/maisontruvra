from flask import Blueprint, request, jsonify
from backend.services.passport_service import PassportService # Assumed service
from backend.utils.sanitization import sanitize_input
from backend.auth.permissions import permissions_required

passport_management_bp = Blueprint('passport_management_bp', __name__, url_prefix='/admin/passports')

# CREATE a new product passport
@passport_management_bp.route('/', methods=['POST'])
@permissions_required('MANAGE_PASSPORTS')
@log_admin_action
@roles_required ('Admin', 'Manager', 'Farmer')
@admin_required
def create_passport():
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Invalid JSON body"), 400

    sanitized_data = sanitize_input(data)

    required_fields = ['product_id', 'token_id']
    if not all(field in sanitized_data for field in required_fields):
        missing = [f for f in required_fields if f not in sanitized_data]
        return jsonify(status="error", message=f"Missing required fields: {', '.join(missing)}"), 400

    try:
        new_passport = PassportService.create_passport(sanitized_data)
        return jsonify(status="success", data=new_passport.to_dict()), 201
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="Failed to create passport."), 500

# READ all product passports (paginated)
@passport_management_bp.route('/', methods=['GET'])
@permissions_required('MANAGE_PASSPORTS')
@staff_required
@admin_required
def get_passports():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        passports_pagination = PassportService.get_all_passports_paginated(page=page, per_page=per_page)
        return jsonify({
            "status": "success",
            "data": [p.to_dict() for p in passports_pagination.items],
            "total": passports_pagination.total,
            "pages": passports_pagination.pages,
            "current_page": passports_pagination.page
        }), 200
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="Failed to retrieve passports."), 500

# READ a single product passport
@passport_management_bp.route('/<int:passport_id>', methods=['GET'])
@permissions_required('MANAGE_PASSPORTS')
@staff_required
@admin_required
def get_passport(passport_id):
    passport = PassportService.get_passport_by_id(passport_id)
    if not passport:
        return jsonify(status="error", message="Passport not found"), 404
    return jsonify(status="success", data=passport.to_dict_full()), 200 # Assumes a more detailed serializer
