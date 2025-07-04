from flask import Blueprint, jsonify, request

from backend.services.email_service import EmailService
from backend.services.newsletter_service import NewsletterService
from backend.utils.decorators import (
    permissions_required,
    roles_required,
)

newsletter_bp = Blueprint(
    "admin_newsletter_routes", __name__, url_prefix="/api/admin/newsletter"
)


# READ all newsletter subscribers
@newsletter_bp.route("/subscribers", methods=["GET"])
@permissions_required("MANAGE_NEWSLETTER")
@roles_required("Admin", "Marketing", "Manager")
def get_subscribers():
    """
    Retrieves all newsletter subscribers.
    ---
    tags:
      - Admin Newsletter
    security:
      - cookieAuth: []
    responses:
      200:
        description: A list of newsletter subscribers.
    """
    subscribers = NewsletterService.get_all_subscribers()
    return jsonify([sub.to_dict() for sub in subscribers])


@newsletter_bp.route("/subscribers/<int:subscriber_id>", methods=["DELETE"])
@permissions_required("MANAGE_NEWSLETTER")
@roles_required("Admin", "Marketing", "Manager")
def delete_subscriber(subscriber_id):
    """
    Deletes a newsletter subscriber.
    ---
    tags:
      - Admin Newsletter
    parameters:
      - in: path
        name: subscriber_id
        required: true
        schema:
          type: integer
    security:
      - cookieAuth: []
    responses:
      200:
        description: Subscriber deleted successfully.
      404:
        description: Subscriber not found.
    """
    if NewsletterService.delete_subscriber_by_id(subscriber_id):
        return jsonify({"message": "Subscriber deleted successfully"})
    return jsonify({"error": "Subscriber not found"}), 404


@newsletter_bp.route("/send", methods=["POST"])
@permissions_required("MANAGE_NEWSLETTER")
@roles_required("Admin", "Marketing", "Manager")
def send_newsletter():
    """
    Sends a newsletter campaign to all subscribers.
    (This is a simplified example; a real implementation would use a task queue like Celery)
    ---
    tags:
      - Admin Newsletter
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              subject:
                type: string
              html_content:
                type: string
    security:
      - cookieAuth: []
    responses:
      200:
        description: Newsletter campaign sent successfully.
      400:
        description: Missing subject or content.
    """
    data = request.get_json()
    subject = data.get("subject")
    html_content = data.get("html_content")

    if not subject or not html_content:
        return jsonify({"error": "Subject and content are required"}), 400

    # In a real app, you would dispatch this to a background task
    # For now, we'll just simulate it
    subscribers = NewsletterService.get_all_subscribers()
    recipient_emails = [sub.email for sub in subscribers]

    # Let's assume a generic sender for now
    sender = "noreply@maisontruvra.com"
    EmailService.send_bulk_email(subject, sender, recipient_emails, html_content)

    return jsonify(
        {"message": f"Newsletter sent to {len(recipient_emails)} subscribers"}
    )
