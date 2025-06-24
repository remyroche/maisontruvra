from flask import Blueprint, request, jsonify
from backend.services.newsletter_service import NewsletterService
from backend.utils.sanitization import sanitize_input
from backend.auth.permissions import admin_required, staff_required, roles_required, permissions_required
from ..utils.decorators import log_admin_action

newsletter_management_bp = Blueprint('newsletter_management_bp', __name__, url_prefix='/admin/newsletter')

# READ all newsletter subscribers
@newsletter_management_bp.route('/subscribers', methods=['GET'])
@permissions_required('MANAGE_NEWSLETTER')
@log_admin_action
@roles_required ('Admin', 'Marketing', 'Manager')
@admin_required
def get_subscribers():
    """
    Get a paginated list of all newsletter subscribers.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        subscribers_pagination = NewsletterService.get_all_subscribers_paginated(page=page, per_page=per_page)
        
        return jsonify({
            "status": "success",
            "data": [s.to_dict() for s in subscribers_pagination.items],
            "total": subscribers_pagination.total,
            "pages": subscribers_pagination.pages,
            "current_page": subscribers_pagination.page
        }), 200
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred while fetching subscribers."), 500

# DELETE a subscriber
@newsletter_management_bp.route('/subscribers/<int:subscriber_id>', methods=['DELETE'])
@permissions_required('MANAGE_NEWSLETTER')
@log_admin_action
@roles_required ('Admin', 'Marketing', 'Manager')
@admin_required
def delete_subscriber(subscriber_id):
    """
    Delete a newsletter subscriber by their ID.
    """
    try:
        if NewsletterService.delete_subscriber(subscriber_id):
            return jsonify(status="success", message="Subscriber deleted successfully."), 200
        else:
            return jsonify(status="error", message="Subscriber not found."), 404
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred while deleting the subscriber."), 500


@newsletter_management_bp.route('/send', methods=['POST'])
@permissions_required('MANAGE_NEWSLETTER')
@log_admin_action
@roles_required ('Admin', 'Marketing', 'Manager')
@admin_required
def send_newsletter():
    """
    Send a new newsletter to a targeted audience.
    This triggers a background task.
    
    Payload Example:
    {
      "subject": "Our New Summer Collection!",
      "content": "<h1>Check it out!</h1>...",
      "target": {
        "list_type": "b2c", // "b2c", "b2b", or "all"
        "tier": ["gold", "silver"] // Optional: list of user tiers
      }
    }
    """
    data = request.get_json()
    if not data or 'subject' not in data or 'content' not in data:
        return jsonify(status="error", message="Subject and content are required."), 400

    sanitized_data = sanitize_input(data)
    # Targeting filters are not sanitized here as they are checked against specific values
    target_filters = data.get('target', {})

    try:
        # This service method would queue the newsletter for sending to the correct segment
        task = NewsletterService.send_newsletter_async(
            sanitized_data['subject'], 
            sanitized_data['content'],
            target_filters
        )
        return jsonify(status="success", message="Newsletter sending has been queued.", data={"task_id": task.id}), 202
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="Failed to queue newsletter for sending."), 500

