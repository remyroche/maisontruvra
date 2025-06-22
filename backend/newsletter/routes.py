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


@admin_bp.route('/newsletters/send', methods=['POST'])
@admin_auth
def send_newsletter():
    """Sends a newsletter to a targeted group of users."""
    data = request.get_json()
    html_content = data.get('htmlContent')
    target_group = data.get('targetGroup')

    # Fetch user emails based on the target group from the DB...
    if target_group == 'b2b_tier_1':
        # db query for tier 1 emails
        pass
    elif target_group == 'all_b2c':
        # db query for B2C emails
        pass
    else:
        return jsonify({'error': 'Invalid target group.'}), 400

    user_emails = [] # From DB
    # Add a job to the queue for each recipient.
    for email in user_emails:
        queue.enqueue('worker.send_email', {'recipient': email, 'body': html_content})

    return jsonify({'message': f'Newsletter dispatch for {len(user_emails)} users has been queued.'}), 202

