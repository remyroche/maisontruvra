# backend/services/email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import List, Optional, Dict, Any

from flask import current_app, render_template, url_for
from flask_mail import Message
from threading import Thread
from backend.extensions import mail
from backend.tasks import send_email_task
from backend.services.monitoring_service import MonitoringService
from flask import render_template, current_app

class EmailService:
    def __init__(self):
        # Email configuration from environment variables
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_username)
        
        if not self.smtp_username or not self.smtp_password:
            MonitoringService.log_warning(
                "SMTP credentials not configured",
                "EmailService"
            )
   

    def send_email(self, to_email: str, subject: str, body: str, 
                   html_body: Optional[str] = None, 
                   attachments: Optional[List[str]] = None) -> Dict[str, Any]:
        """Send an email"""
        try:
            if not self.smtp_username or not self.smtp_password:
                MonitoringService.log_error(
                    "SMTP credentials not configured",
                    "EmailService"
                )
                return {"success": False, "message": "Email service not configured"}
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text body
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML body if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if os.path.isfile(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            
            text = msg.as_string()
            server.sendmail(self.from_email, to_email, text)
            server.quit()
            
            MonitoringService.log_info(
                f"Email sent successfully to {to_email}",
                "EmailService"
            )
            return {"success": True, "message": "Email sent successfully"}
            
        except Exception as e:
            MonitoringService.log_error(
                f"Failed to send email to {to_email}: {str(e)}",
                "EmailService",
                exc_info=True
            )
            return {"success": False, "message": f"Failed to send email: {str(e)}"}
    
    @staticmethod
    def send_email_immediately(recipient, subject, template_name, context):
        """
        Renders the email template and sends the email synchronously.
        
        IMPORTANT: This method should ONLY be called by the 'send_email_task'
        Celery worker in the background. It is not intended for direct use by
        the main application threads.
        """
        html_body = render_template(template_name, **context)
        MonitoringService.log_info(
            f"CELERY WORKER: SIMULATING EMAIL SEND to {recipient}",
            "EmailService"
        )
        # In a real application, the logic to connect to an SMTP server
        # or an email API service (like SendGrid, Mailgun) would be here.
        # Example: mail.send(msg)
        MonitoringService.log_info(
            f"CELERY WORKER: Email to {recipient} sent successfully.",
            "EmailService"
        )
              

    # --- B2C & General User Emails ---
    @staticmethod
    def send_verification_email(user, token):
        """Sends the initial account verification email to a new B2C user."""
        confirmation_link = url_for('auth.confirm_email', token=token, _external=True)
        EmailService.send_email(
            subject="Bienvenue à la Maison Truvrā",
            recipients=[user.email],
            template="welcome_and_verify.html",
            user=user,
            confirmation_link=confirmation_link
        )

    @staticmethod
    def send_b2c_newsletter_confirmation(email):
        """Confirms B2C newsletter subscription."""
        EmailService.send_email(
            subject="Votre inscription à notre journal",
            recipients=[email],
            template="b2c_newsletter_confirmation.html"
        )
    
    @staticmethod
    def send_back_in_stock_email(user, product):
        """Notifies a user that a product they are interested in is back in stock."""
        product_url = url_for('products.get_product', product_id=product.id, _external=True)
        EmailService.send_email(
            subject=f"Votre produit {product.name} est de retour",
            recipients=[user.email],
            template="back_in_stock_notification.html",
            user=user,
            product=product,
            product_url=product_url
        )

    # --- B2B Emails ---
    @staticmethod
    def send_b2b_account_pending_email(user):
        """Informs a B2B user that their application is under review."""
        EmailService.send_email(
            subject="Votre demande de compte professionnel Maison Truvrā",
            recipients=[user.email],
            template="b2b_account_pending.html",
            user=user
        )

    @staticmethod
    def send_b2b_account_approved_email(user):
        """Informs a B2B user that their account has been approved."""
        EmailService.send_email(
            subject="Votre compte professionnel Maison Truvrā est activé",
            recipients=[user.email],
            template="b2b_account_approved.html",
            user=user
        )
    
    @staticmethod
    def send_b2b_newsletter_confirmation(email):
        """Confirms B2B newsletter subscription."""
        EmailService.send_email(
            subject="Confirmation de votre inscription professionnelle",
            recipients=[email],
            template="b2b_newsletter_confirmation.html"
        )

    
    # --- Order Emails (B2C & B2B) ---
    @staticmethod
    def send_order_confirmation_email(order):
        """Sends an order confirmation. Differentiates between B2C and B2B."""
        if order.b2b_account_id:
            user = order.b2b_account.primary_user
            template = "b2b_order_confirmation.html"
            subject = f"Confirmation de votre commande n°{order.id}"
        else:
            user = order.user
            template = "b2c_order_confirmation.html"
            subject = f"Votre commande Maison Truvrā n°{order.id} est confirmée"
        
        EmailService.send_email(subject=subject, recipients=[user.email], template=template, order=order)


    def send_order_confirmation_with_invoice(self, user, order, invoice_pdf_bytes):
        """
        Prepares and sends the order confirmation email with the invoice PDF attached.
        """
        if order.user_type == 'b2c':
            subject = f"Confirmation de votre commande Maison Trüvra #{order.id}"
            template = 'b2c_order_confirmation.html'
        else: # b2b
            subject = f"Confirmation de votre commande B2B Maison Trüvra #{order.id}"
            template = 'b2b_order_confirmation.html'

        # Render the email body
        html_body = render_template(template, user=user, order=order)

        # Prepare the attachment
        attachments = [
            {
                "filename": f"facture-maison-truvra-{order.id}.pdf",
                "content_type": "application/pdf",
                "data": invoice_pdf_bytes
            }
        ]
        
        self.send_email(user.email, subject, html_body, attachments=attachments)

    
    @staticmethod
    def send_order_shipped_email(order, tracking_link, tracking_number):
        """Notifies a user that their order has shipped."""
        user = order.user or order.b2b_account.primary_user
        EmailService.send_email(
            subject="Votre commande Maison Truvrā a été expédiée",
            recipients=[user.email],
            template="order_shipped.html",
            order=order,
            tracking_link=tracking_link,
            tracking_number=tracking_number
        )

    @staticmethod
    def send_order_cancelled_email(order):
        """Confirms to a user that their order has been cancelled."""
        user = order.user or order.b2b_account.primary_user
        EmailService.send_email(
            subject=f"Annulation de votre commande n°{order.id}",
            recipients=[user.email],
            template="order_cancelled.html",
            order=order
        )

    # --- Security & Account Emails (Generic) ---
    @staticmethod
    def send_password_reset_email(user, token, is_b2b=False):
        """Sends a password reset link."""
        if is_b2b:
            # Assuming you have a separate frontend route for B2B password reset
            reset_link = url_for('b2b.reset_password', token=token, _external=True)
        else:
            reset_link = url_for('auth.reset_password', token=token, _external=True)
            
        EmailService.send_email(
            subject="Réinitialisation de votre mot de passe Maison Truvrā",
            recipients=[user.email],
            template="password_reset_request.html",
            user=user,
            reset_link=reset_link
        )

    @staticmethod
    def send_password_change_confirmation(user):
        """Confirms that a user's password has been changed."""
        EmailService.send_email(
            subject="Votre mot de passe a été modifié",
            recipients=[user.email],
            template="password_change_confirmation.html",
            user=user
        )
    
    @staticmethod
    def send_2fa_status_change_email(user, enabled: bool):
        """Confirms that 2FA has been enabled or disabled."""
        template = "2fa_enabled_confirmation.html" if enabled else "2fa_disabled_confirmation.html"
        subject = "Sécurité de votre compte renforcée" if enabled else "Sécurité de votre compte modifiée"
        EmailService.send_email(
            subject=subject,
            recipients=[user.email],
            template=template,
            user=user
        )

    @staticmethod
    def send_security_alert_email(user, ip_address):
        """Sends a security alert for a new device login."""
        from datetime import datetime
        EmailService.send_email(
            subject="Alerte de sécurité : Nouvelle connexion détectée",
            recipients=[user.email],
            template="security_alert.html",
            user=user,
            ip_address=ip_address,
            now=datetime.utcnow()
        )

