from flask import Blueprint, request, jsonify
from backend.services.pos_service import PosService
from backend.utils.input_sanitizer import InputSanitizer
from backend.utils.decorators import staff_required, roles_required, permissions_required

pos_bp = Blueprint('pos_bp', __name__, url_prefix='/admin/pos')

@pos_bp.route('/transaction', methods=['POST'])
@permissions_required('USE_POS')
@roles_required ('Admin', 'Manager', 'Sales')
def create_pos_transaction():
    """
    Create a new Point of Sale transaction.
    """
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Invalid JSON body"), 400

    sanitized_data = InputSanitizer.sanitize_input(data)
    
    required_fields = ['items', 'payment_method', 'terminal_id']
    if not all(field in sanitized_data for field in required_fields):
        missing = [f for f in required_fields if f not in sanitized_data]
        return jsonify(status="error", message=f"Missing required fields: {', '.join(missing)}"), 400

    try:
        # The PoSService should handle inventory checks, payment processing,
        # order creation, and receipt generation.
        order = PosService.create_transaction(sanitized_data)
        return jsonify(status="success", message="Transaction successful.", data=order.to_dict()), 201
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An error occurred while processing the transaction."), 500
