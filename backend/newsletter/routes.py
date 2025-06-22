from flask import Blueprint, request, jsonify
from backend.services.newsletter_service import NewsletterService
from backend.services.exceptions import ServiceException

newsletter_bp = Blueprint('public_newsletter_routes', __name__)

@newsletter_bp.route('/subscribe', methods=['POST'])
def subscribe():
    """
    Subscribes an email to the newsletter.
    """
    data = request.get_json()
    email = data.get('email')
    is_b2b = data.get('is_b2b', False)

    if not email:
        return jsonify({"error": "Email is required."}), 400

    try:
        subscription = NewsletterService.subscribe(email, is_b2b)
        # Trigger a confirmation email task
        from backend.tasks import send_email_task
        template = 'email/b2b_newsletter_subscription.html' if is_b2b else 'email/b2c_newsletter_subscription.html'
        send_email_task.delay(
            to=email,
            subject='Welcome to the Maison Truvra Newsletter!',
            template=template
        )
        return jsonify(subscription.to_dict()), 201
    except ServiceException as e:
        return jsonify({"error": str(e)}), 409 # 409 Conflict for existing email
