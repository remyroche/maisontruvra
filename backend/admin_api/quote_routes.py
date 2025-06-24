from flask import Blueprint, request, jsonify
from backend.services.quote_service import QuoteService
from backend.utils.sanitization import sanitize_input
from backend.auth.permissions import admin_required, staff_required, roles_required, permissions_required
from ..utils.decorators import log_admin_action

quote_management_bp = Blueprint('quote_management_bp', __name__, url_prefix='/admin/quotes')

# READ all quotes (paginated and filterable)
@quote_management_bp.route('/', methods=['GET'])
@permissions_required('MANAGE_QUOTES')
@log_admin_action
@roles_required ('Admin', 'Manager', 'Support')
@admin_required
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
@quote_management_bp.route('/<int:quote_id>', methods=['GET'])
@permissions_required('MANAGE_QUOTES')
@log_admin_action
@roles_required ('Admin', 'Manager', 'Support')
@admin_required
def get_quote(quote_id):
    quote = QuoteService.get_quote_by_id(quote_id)
    if not quote:
        return jsonify(status="error", message="Quote not found"), 404
    return jsonify(status="success", data=quote.to_dict_full()), 200

# UPDATE a quote
@quote_management_bp.route('/<int:quote_id>', methods=['PUT'])
@permissions_required('MANAGE_QUOTES')
@log_admin_action
@roles_required ('Admin', 'Manager', 'Support')
@admin_required
def update_quote(quote_id):
    """
    Update a quote's details or status (e.g., from 'pending' to 'approved').
    """
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Invalid JSON body"), 400
    
    if not QuoteService.get_quote_by_id(quote_id):
        return jsonify(status="error", message="Quote not found"), 404

    sanitized_data = sanitize_input(data)
    try:
        updated_quote = QuoteService.update_quote(quote_id, sanitized_data)
        return jsonify(status="success", data=updated_quote.to_dict()), 200
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="Failed to update quote."), 500

# DELETE a quote
@quote_management_bp.route('/<int:quote_id>', methods=['DELETE'])
@permissions_required('MANAGE_QUOTES')
@log_admin_action
@roles_required ('Admin', 'Manager', 'Support')
@admin_required
def delete_quote(quote_id):
    if not QuoteService.get_quote_by_id(quote_id):
        return jsonify(status="error", message="Quote not found"), 404
    try:
        QuoteService.delete_quote(quote_id)
        return jsonify(status="success", message="Quote deleted successfully."), 200
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="Failed to delete quote."), 500
