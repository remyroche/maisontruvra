from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from backend.utils.csrf_protection import CSRFProtection

csrf_bp = Blueprint("csrf", __name__)


@csrf_bp.route("/csrf-token", methods=["GET"])
@jwt_required()
def get_csrf_token():
    """Generate and return a CSRF token."""
    token = CSRFProtection.generate_csrf_token()
    return jsonify({"csrf_token": token})
