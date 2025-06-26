from backend import create_app, celery
from celery import Celery
from flask import render_template
from playwright.sync_api import sync_playwright
import datetime
import logging

# Set up logger for this module
logger = logging.getLogger(__name__)

def init_celery(app):
    """
    Initializes and configures the Celery instance with the Flask app's settings.
    Also, it wraps tasks to ensure they run within a Flask application context.
    
    Args:
        app: The configured Flask application instance.
    """
    # Update the Celery configuration from the Flask app config.
    # It will automatically look for keys starting with 'CELERY_'.
    celery.config_from_object(app.config, namespace='CELERY')

    class ContextTask(celery.Task):
        """
        A custom Celery Task class that ensures every task is executed
        within a Flask application context. This is crucial for accessing
        the database, configuration, and other Flask extensions within tasks.
        """
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    # Set the custom ContextTask as the default Task class for this Celery instance.
    celery.Task = ContextTask
    
    # This line is important for Celery's auto-discovery of tasks.
    celery.autodiscover_tasks(['backend.tasks'])

    return celery

# Import required services and database
from backend.database import db
from backend.services.email_service import EmailService

@celery.task(name='generate_invoice')
def generate_invoice(order_id):
    """
    Generates a PDF invoice for a given order, using different templates
    for B2B and B2C users. The generated PDF is saved to secure storage.
    """
    logger.info(f"Starting invoice generation for order_id: {order_id}")
    try:
        # 1. Fetch all necessary data for the invoice using SQLAlchemy
        from backend.models.order_models import Order, OrderItem
        from backend.models.user_models import User
        from backend.models.product_models import Product, ProductVariant
        
        # Query using SQLAlchemy ORM
        results = db.session.query(
            Order.id.label('order_id'), Order.created_at, Order.total,
            User.id.label('user_id'), User.name.label('user_name'), User.email, User.role,
            OrderItem.quantity, OrderItem.price_at_purchase,
            ProductVariant.sku, Product.name.label('product_name')
        ).join(User, Order.user_id == User.id)\
         .join(OrderItem, Order.id == OrderItem.order_id)\
         .join(ProductVariant, OrderItem.product_variant_id == ProductVariant.id)\
         .join(Product, ProductVariant.product_id == Product.id)\
         .filter(Order.id == order_id).all()
        
        if not results:
            raise ValueError("Order not found or has no items.")

        # 2. Process data and determine which template to use.
        order_details = results[0]
        user_role = order_details.role
        invoice_template_path = f"invoices/{user_role.lower()}_template.html"
        
        context = {
            "order": order_details,
            "items": results,
            "today": datetime.date.today()
        }

        # 3. Render the HTML template with the order data.
        html_string = render_template(invoice_template_path, **context)

        # 4. Generate the PDF from the rendered HTML.
        pdf_bytes = None # Initialize variable
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # Load the rendered HTML into the headless browser page
            page.set_content(html_string)
            
            # Generate the PDF and store its content (in bytes) in the variable
            pdf_bytes = page.pdf(
                format='A4',
                print_background=True
            )
            browser.close()

        # 5. Save the PDF to a secure storage (placeholder - implement storage service)
        invoice_number = f"INV-{order_details.created_at.year}-{order_id}"
        file_path = f"invoices/{order_details.user_id}/{invoice_number}.pdf"
        
        # TODO: Implement storage service for saving PDFs
        # storage_service.upload(file_path, pdf_bytes, content_type='application/pdf')
        logger.warning("Storage service not implemented - PDF not saved to storage")

        # 6. Save the reference to the invoice in our database using SQLAlchemy
        from backend.models.order_models import Invoice
        
        invoice = Invoice(
            order_id=order_id,
            user_id=order_details.user_id,
            invoice_number=invoice_number,
            file_path=file_path
        )
        db.session.add(invoice)
        db.session.commit()
        logger.info(f"Successfully generated and saved invoice {invoice_number}")

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to generate invoice for order {order_id}: {e}")
        # Re-raise the exception to allow the task queue to handle retries.
        raise

app = create_app()
app.app_context().push()


@celery.task(name='fulfill_order')
def fulfill_order(order_id):
    """
    Main task to fulfill a paid order.
    It retrieves all items for the order and triggers the allocation logic for each.
    """
    logger.info(f"Starting fulfillment for order_id: {order_id}")
    try:
        from backend.models.order_models import Order, OrderItem
        
        # Get order items using SQLAlchemy
        order_items = db.session.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        
        for item in order_items:
            allocate_serialized_items(
                order_item_id=item.id,
                variant_id=item.product_variant_id,
                quantity=item.quantity
            )

        # Once all items are allocated, the order can be moved to 'Awaiting Shipment'.
        order = db.session.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = 'awaiting_shipment'
        
        db.session.commit()
        logger.info(f"Successfully fulfilled and allocated items for order_id: {order_id}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"CRITICAL: Failed to fulfill order {order_id}. Manual intervention required. Error: {e}")
        # Optionally, move order to a 'fulfillment_failed' state.
        raise

def allocate_serialized_items(order_item_id, variant_id, quantity):
    """
    Allocates specific, serialized product items to an order item.
    This creates the full traceability for the Product Passport.
    """
    from backend.models.product_models import ProductItem
    
    # 1. Find available, 'in_stock' serialized items for the given variant.
    #    We use with_for_update() to lock the rows to prevent another process from allocating the same items.
    items_to_allocate = db.session.query(ProductItem)\
        .filter(ProductItem.product_variant_id == variant_id)\
        .filter(ProductItem.status == 'in_stock')\
        .limit(quantity)\
        .with_for_update()\
        .all()

    # 2. Critical check: Ensure the number of physical items matches the quantity ordered.
    if len(items_to_allocate) < quantity:
        # This signifies that inventory_count was out of sync with the actual items.
        # This is a major issue that needs immediate attention.
        raise Exception(f"Inventory mismatch for variant {variant_id}: Wanted {quantity}, found {len(items_to_allocate)}")

    if not items_to_allocate:
        # Should be caught by the check above, but as a safeguard.
        return

    # 3. Update the status of the specific items to 'sold' and link them to the order item.
    for item in items_to_allocate:
        item.status = 'sold'
        item.order_item_id = order_item_id
    
    logger.info(f"Allocated {len(items_to_allocate)} items for order_item_id {order_item_id}")

@celery.task(name='finalize_order')
def finalize_order(order_id):
    """Finalizes an order after successful payment."""
    logger.info(f"Processing 'finalize_order' job for order {order_id}")
    try:
        # 1. Update order status to 'Processing'.
        # 2. Decrement inventory for each item in the order.
        # 3. Award points to the user.
        # All within a single database transaction.

        # Queue subsequent jobs using Celery
        send_email.delay({'type': 'orderConfirmation', 'orderId': order_id})
        generate_invoice.delay(order_id)
    except Exception as e:
        logger.error({'message': f"Job 'finalize_order' failed for order {order_id}", 'error': str(e)})
        raise # Re-raise to allow for retries

@celery.task(name='send_email')
def send_email(email_details):
    """Sends an email via a third-party service."""
    recipient = email_details.get('recipient')
    logger.info(f"Sending email to {recipient}")
    try:
        # Use the EmailService from the project
        EmailService.send_email_immediately(
            recipient=recipient,
            subject=email_details.get('subject', 'Order Confirmation'),
            template_name=email_details.get('template', 'order_confirmation.html'),
            context=email_details.get('context', {})
        )
    except Exception as e:
        logger.error({'message': f"Job 'send_email' failed for recipient {recipient}", 'error': str(e)})
        raise
