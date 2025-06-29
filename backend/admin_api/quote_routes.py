from flask import Blueprint, request, jsonify
from backend.services.quote_service import QuoteService
from backend.services.order_service import OrderService # To convert quote to order
from backend.utils.sanitization import sanitize_input
from backend.utils.decorators import staff_required, roles_required, permissions_required

quote_bp = Blueprint('admin_quote_routes', __name__, url_prefix='/api/admin/quotes')

@quote_bp.route('/', methods=['GET'])
@permissions_required('MANAGE_QUOTES')
@roles_required ('Admin', 'Manager', 'Support')
def get_quotes():
    """Retrieves all quotes."""
    quotes = QuoteService.get_all_quotes()
    return jsonify([q.to_dict() for q in quotes])

@quote_bp.route('/<int:quote_id>', methods=['GET'])
@permissions_required('MANAGE_QUOTES')
@roles_required ('Admin', 'Manager', 'Support')
def get_quote_details(quote_id):
    """Retrieves details for a specific quote."""
    quote = QuoteService.get_quote_by_id(quote_id)
    if not quote:
        return jsonify({"error": "Quote not found"}), 404
    return jsonify(quote.to_dict(include_details=True))

@quote_bp.route('/<int:quote_id>/convert', methods=['POST'])
@permissions_required('MANAGE_QUOTES')
@roles_required ('Admin', 'Manager', 'Support')
def convert_quote_to_order(quote_id):
    """Converts a quote into a draft order."""
    try:
        order = OrderService.create_order_from_quote(quote_id)
        if not order:
            return jsonify({"error": "Failed to convert quote"}), 400
        return jsonify(order.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quote_bp.route('/<int:quote_id>', methods=['DELETE'])
@permissions_required('MANAGE_QUOTES')
@roles_required ('Admin', 'Manager', 'Support')
def delete_quote(quote_id):
    """Deletes a quote."""
    if QuoteService.delete_quote(quote_id):
        return jsonify({"message": "Quote deleted successfully"})
    return jsonify({"error": "Quote not found"}), 404

@quote_bp.route('/', methods=['GET'])
@permissions_required('MANAGE_QUOTES')
@roles_required ('Admin', 'Manager', 'Support')
def get_quotes():
    """
    Get a paginated list of all B2B quotes.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = sanitize_input(request.args.get('status'))
        filters = {'status': status} if status else {}

        quotes_pagination = QuoteService.get_all_quotes_paginated(page=page, per_page=per_page, filters=filters)
        
        return jsonify({
            "status": "success",
            "data": [q.to_dict() for q in quotes_pagination.items],
            "total": quotes_pagination.total,
            "pages": quotes_pagination.pages,
            "current_page": quotes_pagination.page
        }), 200
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred while fetching quotes."), 500

# READ a single quote
@quote_bp.route('/<int:quote_id>', methods=['GET'])
@permissions_required('MANAGE_QUOTES')
@roles_required ('Admin', 'Manager', 'Support')
def get_quote(quote_id):
    quote = QuoteService.get_quote_by_id(quote_id)
    if not quote:
        return jsonify(status="error", message="Quote not found"), 404
    return jsonify(status="success", data=quote.to_dict_full()), 200

