# backend/services/email_service.py
from flask import current_app, render_template, url_for
from flask_mail import Message
from threading import Thread
from backend.extensions import mail

# Asynchronous email sending function to avoid blocking requests.
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipients, template, **kwargs):
    """
    Generic function to send an email asynchronously.
    
    :param subject: Email subject.
    :param recipients: List of recipient email addresses.
    :param template: The name of the HTML template file in the /templates folder.
    :param kwargs: Keyword arguments to pass to the template for rendering.
    """
    app = current_app._get_current_object()
    msg = Message(subject, recipients=recipients)
    
    # Add logo URL to the template context
    if 'logo_url' not in kwargs:
        kwargs['logo_url'] = url_for('static', filename='images/logo_email.png', _external=True)

    msg.html = render_template(template, **kwargs)
    
    # Start a new thread to send the email in the background
    thread = Thread(target=send_async_email, args=[app, msg])
    thread.start()
    return thread

class EmailService:
    """A centralized service for all application email notifications."""

    # --- B2C & General User Emails ---
    @staticmethod
    def send_verification_email(user, token):
        """Sends the initial account verification email to a new B2C user."""
        confirmation_link = url_for('auth.confirm_email', token=token, _external=True)
        send_email(
            subject="Bienvenue à la Maison Truvrā",
            recipients=[user.email],
            template="welcome_and_verify.html",
            user=user,
            confirmation_link=confirmation_link
        )

    @staticmethod
    def send_b2c_newsletter_confirmation(email):
        """Confirms B2C newsletter subscription."""
        send_email(
            subject="Votre inscription à notre journal",
            recipients=[email],
            template="b2c_newsletter_confirmation.html"
        )
    
    @staticmethod
    def send_back_in_stock_email(user, product):
        """Notifies a user that a product they are interested in is back in stock."""
        product_url = url_for('products.get_product', product_id=product.id, _external=True)
        send_email(
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
        send_email(
            subject="Votre demande de compte professionnel Maison Truvrā",
            recipients=[user.email],
            template="b2b_account_pending.html",
            user=user
        )

    @staticmethod
    def send_b2b_account_approved_email(user):
        """Informs a B2B user that their account has been approved."""
        send_email(
            subject="Votre compte professionnel Maison Truvrā est activé",
            recipients=[user.email],
            template="b2b_account_approved.html",
            user=user
        )
    
    @staticmethod
    def send_b2b_newsletter_confirmation(email):
        """Confirms B2B newsletter subscription."""
        send_email(
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
        
        send_email(subject=subject, recipients=[user.email], template=template, order=order)

    @staticmethod
    def send_order_shipped_email(order, tracking_link, tracking_number):
        """Notifies a user that their order has shipped."""
        user = order.user or order.b2b_account.primary_user
        send_email(
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
        send_email(
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
            
        send_email(
            subject="Réinitialisation de votre mot de passe Maison Truvrā",
            recipients=[user.email],
            template="password_reset_request.html",
            user=user,
            reset_link=reset_link
        )

    @staticmethod
    def send_password_change_confirmation(user):
        """Confirms that a user's password has been changed."""
        send_email(
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
        send_email(
            subject=subject,
            recipients=[user.email],
            template=template,
            user=user
        )

    @staticmethod
    def send_security_alert_email(user, ip_address):
        """Sends a security alert for a new device login."""
        from datetime import datetime
        send_email(
            subject="Alerte de sécurité : Nouvelle connexion détectée",
            recipients=[user.email],
            template="security_alert.html",
            user=user,
            ip_address=ip_address,
            now=datetime.utcnow()
        )

