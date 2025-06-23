from flask_mail import Message
from flask import render_template
from backend.extensions import mail

class EmailService:
    @staticmethod
    def send_order_confirmation(order, pdf_attachment_data, pdf_filename):
        """
        Sends an order confirmation email, choosing the template based on user type
        and attaching the generated invoice/receipt PDF.
        """
        user = order.user
        subject = f"Confirmation de votre commande #{order.id}"
        
        # Choose the email template based on the user's type
        if user and user.user_type == 'B2B':
            template_name = 'emails/b2b_order_confirmation.html'
            # The B2B email might have more formal language or different info
        else:
            template_name = 'emails/b2c_order_confirmation.html'

        # Render the email body from the template
        html_body = render_template(template_name, order=order)
        
        # Create the email message
        msg = Message(
            subject=subject,
            recipients=[user.email],
            html=html_body
        )

        # Attach the invoice PDF
        msg.attach(
            filename=pdf_filename,
            content_type='application/pdf',
            data=pdf_attachment_data
        )
        
        # Send the email
        mail.send(msg)



