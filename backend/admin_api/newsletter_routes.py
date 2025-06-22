from flask import Blueprint, request, jsonify
from backend.services.newsletter_service import NewsletterService
from backend.auth.permissions import admin_required, permission_required, Permission

newsletter_routes = Blueprint('admin_newsletter_routes', __name__)

@permission_required(Permission.MANAGE_NEWSLETTER)
@newsletter_routes.route('/newsletter/subscribers', methods=['GET'])
@admin_required
def get_subscribers():
    subscribers = NewsletterService.get_all_subscribers()
    return jsonify([s.to_dict() for s in subscribers]), 200

@permission_required(Permission.MANAGE_NEWSLETTER)
@newsletter_routes.route('/newsletter/send', methods=['POST'])
@admin_required
def send_newsletter():
    data = request.get_json()
    subject = data.get('subject')
    content = data.get('content')
    
    if not subject or not content:
        return jsonify({"error": "Subject and content are required."}), 400
        
    # This triggers an async task
    NewsletterService.send_newsletter_to_all(subject, content)
    
    return jsonify({"message": "Newsletter sending process has been initiated."}), 202
