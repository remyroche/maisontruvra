from flask_mail import Message
from flask import render_template, current_app
from datetime import datetime

from backend.extensions import mail
from backend.models.user_models import User
from backend.models.order_models import Order

class EmailService:
    """
    A unified service to handle the sending of all transactional and marketing emails.
    """

    @staticmethod
    def _send_email(subject: str, recipients: list, template: str, context: dict, attachment: dict = None):
        """
        A generic, internal function to render and send an email.

        Args:
            subject (str): The subject line of the email.
            recipients (list): A list of recipient email addresses.
            template (str): The path to the HTML template file.
            context (dict): A dictionary of data to pass to the template.
            attachment (dict, optional): A dictionary with attachment details 
                                         {'filename': str, 'mimetype': str, 'data': bytes}.
        """
        try:
            # Render the HTML body of the email using the provided template and context
            html_body = render_template(template, **context)
            
            msg = Message(
                subject=subject,
                recipients=recipients,
                html=html_body,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER')
            )

            # If an attachment is provided, add it to the message
            if attachment:
                msg.attach(
                    filename=attachment['filename'],
                    content_type=attachment['mimetype'],
                    data=attachment['data']
                )
            
            # Send the email using the Flask-Mail extension
            mail.send(msg)
            current_app.logger.info(f"Email '{subject}' sent to {recipients}")

        except Exception as e:
            current_app.logger.error(f"Failed to send email to {recipients}: {e}")
            # In a production environment, you might want to add this task to a retry queue.
            
    # --- Account Management Emails ---

    @staticmethod
    def send_welcome_and_verification(user: User, verification_token: str):
        verification_url = f"{current_app.config['BASE_URL']}/verify-email?token={verification_token}"
        EmailService._send_email(
            subject="Bienvenue chez Maison Trüvra ! Confirmez votre e-mail",
            recipients=[user.email],
            template="emails/welcome_and_verify.html",
            context={"user": user, "verification_url": verification_url}
        )
        
    @staticmethod
    def send_b2b_pending_approval(user: User):
        EmailService._send_email(
            subject="Votre demande de compte professionnel a été reçue",
            recipients=[user.email],
            template="emails/b2b_account_pending.html",
            context={"user": user}
        )

    @staticmethod
    def send_b2b_account_approved(user: User):
        login_url = f"{current_app.config['BASE_URL']}/pro/login.html"
        EmailService._send_email(
            subject="Votre compte professionnel Maison Trüvra est approuvé !",
            recipients=[user.email],
            template="emails/b2b_account_approved.html",
            context={"user": user, "login_url": login_url}
        )

    @staticmethod
    def send_password_reset(user: User, reset_token: str):
        reset_url = f"{current_app.config['BASE_URL']}/reset-password?token={reset_token}"
        EmailService._send_email(
            subject="Réinitialisation de votre mot de passe - Maison Trüvra",
            recipients=[user.email],
            template="emails/password_reset.html",
            context={"reset_url": reset_url}
        )


    @staticmethod
    def send_password_change(user: User, reset_token: str):
        reset_url = f"{current_app.config['BASE_URL']}/reset-password?token={reset_token}"
        EmailService._send_email(
            subject="Votre mot de passe a bien été changé - Maison Trüvra",
            recipients=[user.email],
            template="emails/password_change.html",
            context={"reset_url": reset_url}
        )
        
    @staticmethod
    def send_security_alert(user: User, action_description: str):
        """A generic function for sending security-related notifications."""
        context = {
            "user": user,
            "action_description": action_description,
            "timestamp": datetime.utcnow().strftime('%d/%m/%Y à %H:%M:%S UTC')
        }
        EmailService._send_email(
            subject="Alerte de Sécurité concernant votre compte Maison Trüvra",
            recipients=[user.email],
            template="emails/security_alert.html",
            context=context
        )

    # --- Order & Invoice Emails ---

    @staticmethod
    def send_order_confirmation(order: Order, pdf_attachment_data: bytes, pdf_filename: str):
        """Sends an order confirmation with the correct invoice/receipt attached."""
        user = order.user
        
        if user and user.user_type == 'B2B':
            subject = f"Facture pour votre commande Maison Trüvra n°{order.id}"
            template = 'emails/b2b_order_confirmation.html'
        else:
            subject = f"Confirmation de votre commande Maison Trüvra n°{order.id}"
            template = 'emails/b2c_order_confirmation.html'
        
        context = {
            "user": user, "order": order,
            "dashboard_url": f"{current_app.config['BASE_URL']}/pro/dashboard"
        }
        attachment = {"filename": pdf_filename, "mimetype": 'application/pdf', "data": pdf_attachment_data}
        
        EmailService._send_email(subject, [user.email], template, context, attachment)

    @staticmethod
    def send_order_shipped(order: Order, tracking_number: str, tracking_url: str):
        subject = f"Votre commande Maison Trüvra n°{order.id} a été expédiée !"
        context = {"user": order.user, "order": order, "tracking_number": tracking_number, "tracking_url": tracking_url}
        EmailService._send_email(subject, [order.user.email], 'emails/order_shipped.html', context)

    @staticmethod
    def send_order_cancelled(order: Order):
        subject = f"Annulation de votre commande Maison Trüvra n°{order.id}"
        context = {"user": order.user, "order": order}
        EmailService._send_email(subject, [order.user.email], 'emails/order_cancelled.html', context)
        
    # --- Marketing Emails ---

    @staticmethod
    def send_b2c_newsletter_confirmation(user_email: str):
        EmailService._send_email(
            subject="Confirmation de votre abonnement à la newsletter Maison Trüvra",
            recipients=[user_email],
            template="emails/newsletter/b2c_newsletter_confirmation.html",
            context={}
        )

    @staticmethod
    def send_b2b_newsletter_confirmation(user_email: str):
        EmailService._send_email(
            subject="Confirmation de votre abonnement à la newsletter Maison Trüvra",
            recipients=[user_email],
            template="emails/newsletter/b2b_newsletter_confirmation.html",
            context={}
        )

