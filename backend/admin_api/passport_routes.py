from flask import Blueprint, jsonify
from backend.services.passport_service import PassportService
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from backend.auth.permissions import permission_required, Permission, admin_required
from backend.models.passport_models import ProductPassport
from backend.extensions import db

passport_bp = Blueprint('admin_passport_bp', __name__, url_prefix='/passports')

@passport_bp.route('/', methods=['POST'])
@jwt_required()
@permission_required(Permission.MANAGE_PASSPORTS)
def create_passport():
    data = request.get_json()
    # Add validation for required fields
    new_passport = ProductPassport(**data)
    db.session.add(new_passport)
    db.session.commit()
    return jsonify(new_passport.to_dict()), 201


