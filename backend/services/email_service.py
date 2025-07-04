# backend/services/email_service.py
import os

from flask import current_app, render_template, url_for
from flask_mail import Message
from backend.extensions import mail
from backend.services.monitoring_service import MonitoringService


class EmailService:
    def __init__(self):
        # Email configuration from environment variables
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)

        if not self.smtp_username or not self.smtp_password:
            MonitoringService.log_warning(
                "SMTP credentials not configured", "EmailService"
            )

    @staticmethod
    def send_email(to, subject, template, **kwargs):
        """Generic email sending function."""
        msg = Message(
            subject,
            recipients=[to],
            html=render_template(template, **kwargs),
            sender=current_app.config["MAIL_DEFAULT_SENDER"],
        )
        mail.send(msg)

    @staticmethod
    def send_email_immediately(recipient, subject, template_name, context):
        """
        Renders the email template and sends the email synchronously.

        IMPORTANT: This method should ONLY be called by the 'send_email_task'
        Celery worker in the background. It is not intended for direct use by
        the main application threads.
        """
        render_template(template_name, **context)
        MonitoringService.log_info(
            f"CELERY WORKER: SIMULATING EMAIL SEND to {recipient}", "EmailService"
        )
        # In a real application, the logic to connect to an SMTP server
        # or an email API service (like SendGrid, Mailgun) would be here.
        # Example: mail.send(msg)
        MonitoringService.log_info(
            f"CELERY WORKER: Email to {recipient} sent successfully.", "EmailService"
        )

    # --- B2C & General User Emails ---
    @staticmethod
    def send_verification_email(user, token):
        """Sends the initial account verification email to a new B2C user."""
        confirmation_link = url_for(
            "unified_auth.verify_email", token=token, _external=True
        )
        EmailService.send_email(
            to=user.email,
            subject="Bienvenue à la Maison Truvrā",
            template="welcome_and_verify.html",
            user=user,
            confirmation_link=confirmation_link,
        )

    @staticmethod
    def send_b2c_newsletter_confirmation(email):
        """Confirms B2C newsletter subscription."""
        EmailService.send_email(
            to=email,
            subject="Votre inscription à notre journal",
            template="b2c_newsletter_confirmation.html",
        )

    @staticmethod
    def send_back_in_stock_email(user, product):
        """Notifies a user that a product they are interested in is back in stock."""
        product_url = url_for(
            "products.get_product", product_id=product.id, _external=True
        )
        EmailService.send_email(
            to=user.email,
            subject=f"Votre produit {product.name} est de retour",
            template="back_in_stock_notification.html",
            user=user,
            product=product,
            product_url=product_url,
        )

    # --- B2B Emails ---
    @staticmethod
    def send_b2b_account_pending_email(user):
        """Informs a B2B user that their application is under review."""
        EmailService.send_email(
            to=user.email,
            subject="Votre demande de compte professionnel Maison Truvrā",
            template="b2b_account_pending.html",
            user=user,
        )

    @staticmethod
    def send_b2b_account_approved_email(user):
        """Informs a B2B user that their account has been approved."""
        EmailService.send_email(
            to=user.email,
            subject="Votre compte professionnel Maison Truvrā est activé",
            template="b2b_account_approved.html",
            user=user,
        )

    @staticmethod
    def send_b2b_newsletter_confirmation(email):
        """Confirms B2B newsletter subscription."""
        EmailService.send_email(
            to=email,
            subject="Confirmation de votre inscription professionnelle",
            template="b2b_newsletter_confirmation.html",
        )

    @staticmethod
    def send_b2b_application_rejected_email(email, name, reason):
        """Informs a user that their B2B application has been rejected."""
        EmailService.send_email(
            to=email,
            subject="Votre demande de partenariat professionnel",
            template="b2b_application_rejected.html",
            name=name,
            reason=reason,
        )

    # --- Order Emails (B2C & B2B) ---
    @staticmethod
    def send_order_confirmation(order):
        """Sends an order confirmation. Differentiates between B2C and B2B."""
        if order.b2b_account_id:
            user = order.b2b_account.primary_user
            template = "b2b_order_confirmation.html"
            subject = f"Confirmation de votre commande n°{order.id}"
        else:
            user = order.user
            template = "b2c_order_confirmation.html"
            subject = f"Votre commande Maison Truvrā n°{order.id} est confirmée"

        EmailService.send_email(
            to=user.email, subject=subject, template=template, order=order
        )

    def send_order_confirmation_with_invoice(self, user, order, invoice_pdf_bytes):
        """
        Prepares and sends the order confirmation email with the invoice PDF attached.
        """
        if order.user_type == "b2c":
            subject = f"Confirmation de votre commande Maison Trüvra #{order.id}"
            template = "b2c_order_confirmation.html"
        else:  # b2b
            subject = f"Confirmation de votre commande B2B Maison Trüvra #{order.id}"
            template = "b2b_order_confirmation.html"

        # Render the email body
        html_body = render_template(template, user=user, order=order)

        # Prepare the attachment
        attachments = [
            {
                "filename": f"facture-maison-truvra-{order.id}.pdf",
                "content_type": "application/pdf",
                "data": invoice_pdf_bytes,
            }
        ]

        self.send_email(user.email, subject, html_body, attachments=attachments)

    @staticmethod
    def send_order_shipped_email(order, tracking_link, tracking_number):
        """Notifies a user that their order has shipped."""
        user = order.user or order.b2b_account.primary_user
        EmailService.send_email(
            to=user.email,
            subject="Votre commande Maison Truvrā a été expédiée",
            template="order_shipped.html",
            order=order,
            tracking_link=tracking_link,
            tracking_number=tracking_number,
        )

    @staticmethod
    def send_order_cancelled_email(order):
        """Confirms to a user that their order has been cancelled."""
        user = order.user or order.b2b_account.primary_user
        EmailService.send_email(
            to=user.email,
            subject=f"Annulation de votre commande n°{order.id}",
            template="order_cancelled.html",
            order=order,
        )

    # --- Security & Account Emails (Generic) ---
    @staticmethod
    def send_password_reset_email(user, token, admin_triggered=False):
        """
        Sends a password reset link.

        Args:
            user: User object
            token: Password reset token
            admin_triggered: Whether this reset was triggered by an admin
        """
        # Create frontend reset link with token
        reset_link = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={token}"

        subject = "Réinitialisation de votre mot de passe Maison Truvrā"
        if admin_triggered:
            subject = "Réinitialisation de votre mot de passe par l'administrateur"

        EmailService.send_email(
            to=user.email,
            subject=subject,
            template="password_reset_request.html",
            user=user,
            reset_link=reset_link,
            admin_triggered=admin_triggered,
        )

    @staticmethod
    def send_password_change_confirmation(user):
        """Confirms that a user's password has been changed."""
        EmailService.send_email(
            to=user.email,
            subject="Votre mot de passe a été modifié",
            template="password_change_confirmation.html",
            user=user,
        )

    @staticmethod
    def send_2fa_status_change_email(user, enabled: bool, admin_triggered=False):
        """
        Confirms that 2FA has been enabled or disabled.

        Args:
            user: User object
            enabled: Whether 2FA was enabled (True) or disabled (False)
            admin_triggered: Whether this change was triggered by an admin
        """
        template = (
            "2fa_enabled_confirmation.html"
            if enabled
            else "2fa_disabled_confirmation.html"
        )
        subject = (
            "Sécurité de votre compte renforcée"
            if enabled
            else "Sécurité de votre compte modifiée"
        )

        if admin_triggered:
            subject = "Modification de la sécurité de votre compte par l'administrateur"

        EmailService.send_email(
            to=user.email,
            subject=subject,
            template=template,
            user=user,
            admin_triggered=admin_triggered,
        )

    @staticmethod
    def send_security_alert_email(user, ip_address):
        """Sends a security alert for a new device login."""
        from datetime import datetime

        EmailService.send_email(
            to=user.email,
            subject="Alerte de sécurité : Nouvelle connexion détectée",
            template="security_alert.html",
            user=user,
            ip_address=ip_address,
            now=datetime.utcnow(),
        )
