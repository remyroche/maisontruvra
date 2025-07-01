from .. import db
from ..models.utility_models import ContactMessage
from .background_task_service import BackgroundTaskService
from flask import current_app
from backend.services.email_service import EmailService

class ContactService:
    def __init__(self, logger):
        self.logger = logger
        self.email_service = EmailService(logger)

    def submit_contact_form(self, form_data):
        """
        Handles contact form submission by sending an email to the site admin.
        """
        try:
            name = form_data.get('name')
            email = form_data.get('email')
            form_subject = form_data.get('subject')
            message = form_data.get('message')

            # Email to be sent to the admin
            admin_email = current_app.config.get('ADMIN_EMAIL')
            if not admin_email:
                self.logger.error("ADMIN_EMAIL not configured. Cannot send contact form email.")
                return False

            subject = f"New Contact Form Submission: {form_subject}"
            
            # Using a base email template to send the content
            template = "b2c_base_template"
            body_content = f"""
                <h3>You have received a new message from your website contact form.</h3>
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Subject:</strong> {form_subject}</p>
                <p><strong>Message:</strong></p>
                <p>{message}</p>
            """
            context = {"body_content": body_content}
            
            self.email_service.send_email(admin_email, subject, template, context)

            self.logger.info(f"Contact form submission from {email} sent to admin.")
            
            # Optionally, send a confirmation email to the user
            # user_subject = "We've received your message"
            # user_template = "contact_confirmation" # A new template would be needed
            # self.email_service.send_email(email, user_subject, user_template, {"name": name})

            return True
        except Exception as e:
            self.logger.error(f"Failed to process contact form submission: {e}")
            return False


    
    def create_contact_message(data):
        """
        Saves a new contact message to the database and triggers notification emails.
        """
        # Data is assumed to be validated by a Marshmallow schema in the route.
        
        contact_message = ContactMessage(
            name=data['name'],
            email=data['email'],
            subject=data['subject'],
            message=data['message']
        )
        db.session.add(contact_message)
        db.session.commit()

        # Queue an acknowledgement email to the user.
        # This will run in the background via the Celery worker.
        # Note: You will need to create the 'emails/contact_confirmation.html' template.
        BackgroundTaskService.send_email_async.delay(
            recipients=[data['email']],
            subject='We have received your message',
            template='emails/contact_confirmation',
            context={'name': data['name']}
        )

        # Queue a notification email to the site administrator.
        # Note: You will need to create the 'emails/admin_contact_notification.html' template
        # and set ADMIN_EMAIL in your application config.
        admin_email = current_app.config.get('ADMIN_EMAIL')
        if admin_email:
            BackgroundTaskService.send_email_async.delay(
                recipients=[admin_email],
                subject=f"New Contact Form Submission: {data['subject']}",
                template='emails/admin_contact_notification',
                context={'data': data}
            )

        return contact_message
