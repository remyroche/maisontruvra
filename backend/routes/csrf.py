
from flask import Blueprint, jsonify
from backend.utils.csrf_protection import CSRFProtection

csrf_bp = Blueprint('csrf', __name__)

@csrf_bp.route('/csrf-token', methods=['GET'])
def get_csrf_token():
    """Get CSRF token for frontend."""
    token = CSRFProtection.generate_csrf_token()
    return jsonify({'csrf_token': token})
