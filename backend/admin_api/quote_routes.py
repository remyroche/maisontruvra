from flask import Blueprint, jsonify
from backend.services.request_management_service import RequestManagementService
from backend.auth.permissions import admin_required

quote_routes = Blueprint('admin_quote_routes', __name__)

@quote_routes.route('/quotes', methods=['GET'])
@admin_required
def get_all_quotes():
    """
    Retrieves all quote requests.
    """
    quotes = RequestManagementService.get_all_requests_by_type('quote')
    return jsonify([q.to_dict() for q in quotes]), 200

@quote_routes.route('/quotes/<int:quote_id>/respond', methods=['POST'])
@admin_required
def respond_to_quote(quote_id):
    """
    Allows an admin to respond to a quote request.
    This would typically involve sending an email with pricing details.
    """
    # Simplified logic
    # In a real app, this would trigger an email with a custom message.
    quote = RequestManagementService.get_request_by_id(quote_id)
    if quote and quote.request_type == 'quote':
        # Mark as responded
        RequestManagementService.update_request_status(quote_id, 'Responded')
        return jsonify({"message": f"Quote {quote_id} has been marked as responded."}), 200
    return jsonify({"error": "Quote not found"}), 404