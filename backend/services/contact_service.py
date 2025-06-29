from .. import db
from ..models.utility_models import ContactMessage
from .background_task_service import BackgroundTaskService
from flask import current_app

class ContactService:
    @staticmethod
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