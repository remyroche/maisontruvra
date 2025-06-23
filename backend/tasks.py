from backend.extensions import celery
from backend.services.email_service import EmailService
from backend.services.b2b_loyalty_service import B2BLoyaltyService
from flask import current_app


@celery.task(name='tasks.expire_points')
def expire_points():
    """
    Celery task to expire loyalty points older than one year.
    """
    with current_app.app_context():
        count = LoyaltyService.expire_points_task()
        current_app.logger.info(f"Expired {count} loyalty point transactions.")
        return count

@celery.task(name='tasks.update_tiers')
def update_tiers():
    """
    Celery task to recalculate and update B2B user loyalty tiers.
    """
    with current_app.app_context():
        count = LoyaltyService.update_user_tiers_task()
        current_app.logger.info(f"Updated loyalty tiers for {count} active B2B users.")
        return count

@celery_app.task(name='tasks.send_email')
def send_email_task(to, subject, html_body):
    """
    Celery task to send an email.
    This runs in the background, so the application doesn't block.
    """
    # The application context is required to access `current_app` and `mail`
    app = celery_app.flask_app
    with app.app_context():
        try:
            msg = Message(
                subject,
                recipients=[to],
                html=html_body,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            mail.send(msg)
            current_app.logger.info(f"Email successfully sent to {to}")
        except Exception as e:
            current_app.logger.error(f"Failed to send email to {to}: {str(e)}")
            # You might want to add retry logic here
            # For example: self.retry(exc=e, countdown=60)

@celery_app.task(name='tasks.generate_invoice_pdf')
def generate_invoice_pdf_task(order_id):
    """
    Celery task to generate a PDF invoice for an order.
    """
    app = celery_app.flask_app
    with app.app_context():
        # This is a placeholder for your actual PDF generation logic
        # You would typically query the order, render an HTML template,
        # and then use a library like WeasyPrint to create the PDF.
        current_app.logger.info(f"Generating invoice PDF for order {order_id}...")
        # from .services.invoice_service import generate_invoice_pdf_data
        # data = generate_invoice_pdf_data(order_id)
        # html = render_template('non-email/b2c_invoice.html', **data)
        # pdf = weasyprint.HTML(string=html).write_pdf()
        # save_pdf_to_storage(pdf, f"invoice_{order_id}.pdf")
        current_app.logger.info(f"Successfully generated invoice for order {order_id}")


@celery_app.task(name='tasks.generate_passport_pdf')
def generate_passport_pdf_task(passport_id):
    """
    Celery task to generate a product passport PDF.
    """
    app = celery_app.flask_app
    with app.app_context():
        # Placeholder for PDF generation logic
        current_app.logger.info(f"Generating product passport PDF for {passport_id}...")
        # Logic to fetch passport data and render a PDF
        current_app.logger.info(f"Successfully generated passport for {passport_id}")

@celery.task(name='app.update_b2b_loyalty_tiers')
def update_b2b_loyalty_tiers_task():
    """
    Celery task to periodically update B2B loyalty tiers.
    """
    try:
        current_app.logger.info("Starting scheduled task: update_b2b_loyalty_tiers_task")
        B2BLoyaltyService._calculate_and_assign_tiers()
        current_app.logger.info("Finished scheduled task: update_b2b_loyalty_tiers_task")
        return "B2B loyalty tiers updated successfully."
    except Exception as e:
        current_app.logger.error(f"Scheduled task update_b2b_loyalty_tiers_task failed: {e}", exc_info=True)
        raise update_b2b_loyalty_tiers_task.retry(exc=e, countdown=3600) # Retry after 1 hour

# Example of how you might schedule this task in your Celery beat configuration:
# celery.conf.beat_schedule = {
#     'update-b2b-tiers-every-day': {
#         'task': 'app.update_b2b_loyalty_tiers',
#         'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
#     },
# }
