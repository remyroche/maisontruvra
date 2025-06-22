from backend import create_app, celery

from flask import render_template
import weasyprint
import datetime

# Assume 'queue' is a configured task queue instance (e.g., Celery app)
# Assume 'db', 'logger', and 'storage_service' (for S3) are configured.

@queue.task(name='generate_invoice')
def generate_invoice(order_id):
    """
    Generates a PDF invoice for a given order, using different templates
    for B2B and B2C users. The generated PDF is saved to secure storage.
    """
    logger.info(f"Starting invoice generation for order_id: {order_id}")
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Fetch all necessary data for the invoice in one go.
        cursor.execute(
            """
            SELECT
                o.id as order_id, o.created_at, o.total,
                u.id as user_id, u.name as user_name, u.email, u.role,
                oi.quantity, oi.price_at_purchase,
                pv.sku, p.name as product_name
            FROM orders o
            JOIN users u ON o.user_id = u.id
            JOIN order_items oi ON o.id = oi.order_id
            JOIN product_variants pv ON oi.product_variant_id = pv.id
            JOIN products p ON pv.product_id = p.id
            WHERE o.id = %s
            """,
            (order_id,)
        )
        results = cursor.fetchall()
        if not results:
            raise ValueError("Order not found or has no items.")

        # 2. Process data and determine which template to use.
        order_details = results[0]
        user_role = order_details['role']
        invoice_template_path = f"invoices/{user_role.lower()}_template.html"
        
        context = {
            "order": order_details,
            "items": results,
            "today": datetime.date.today()
        }

        # 3. Render the HTML template with the order data.
        html_string = render_template(invoice_template_path, **context)

        # 4. Generate the PDF from the rendered HTML.
        pdf_bytes = weasyprint.HTML(string=html_string).write_pdf()

        # 5. Save the PDF to a secure storage (like a private S3 bucket).
        invoice_number = f"INV-{order_details['created_at'].year}-{order_id}"
        file_path = f"invoices/{user_id}/{invoice_number}.pdf"
        storage_service.upload(file_path, pdf_bytes, content_type='application/pdf')

        # 6. Save the reference to the invoice in our database.
        cursor.execute(
            """
            INSERT INTO invoices (order_id, user_id, invoice_number, file_path)
            VALUES (%s, %s, %s, %s)
            """,
            (order_id, order_details['user_id'], invoice_number, file_path)
        )
        conn.commit()
        logger.info(f"Successfully generated and saved invoice {invoice_number}")

    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to generate invoice for order {order_id}: {e}")
        # Re-raise the exception to allow the task queue to handle retries.
        raise
    finally:
        cursor.close()
        conn.close()

app = create_app()
app.app_context().push()


@queue.task(name='fulfill_order')
def fulfill_order(order_id):
    """
    Main task to fulfill a paid order.
    It retrieves all items for the order and triggers the allocation logic for each.
    """
    logger.info(f"Starting fulfillment for order_id: {order_id}")
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, product_variant_id, quantity FROM order_items WHERE order_id = %s",
            (order_id,)
        )
        order_items = cursor.fetchall()
        
        for item in order_items:
            allocate_serialized_items(
                order_item_id=item['id'],
                variant_id=item['product_variant_id'],
                quantity=item['quantity'],
                cursor=cursor # Pass the cursor to run in the same transaction
            )

        # Once all items are allocated, the order can be moved to 'Awaiting Shipment'.
        cursor.execute("UPDATE orders SET status = 'awaiting_shipment' WHERE id = %s", (order_id,))
        
        conn.commit()
        logger.info(f"Successfully fulfilled and allocated items for order_id: {order_id}")
    except Exception as e:
        conn.rollback()
        logger.error(f"CRITICAL: Failed to fulfill order {order_id}. Manual intervention required. Error: {e}")
        # Optionally, move order to a 'fulfillment_failed' state.
    finally:
        cursor.close()
        conn.close()

def allocate_serialized_items(order_item_id, variant_id, quantity, cursor):
    """
    Allocates specific, serialized product items to an order item.
    This creates the full traceability for the Product Passport.
    """
    # 1. Find available, 'in_stock' serialized items for the given variant.
    #    We lock the rows to prevent another process from allocating the same items.
    cursor.execute(
        "SELECT id FROM product_items WHERE product_variant_id = %s AND status = 'in_stock' LIMIT %s FOR UPDATE",
        (variant_id, quantity)
    )
    items_to_allocate = cursor.fetchall()

    # 2. Critical check: Ensure the number of physical items matches the quantity ordered.
    if len(items_to_allocate) < quantity:
        # This signifies that inventory_count was out of sync with the actual items.
        # This is a major issue that needs immediate attention.
        raise Exception(f"Inventory mismatch for variant {variant_id}: Wanted {quantity}, found {len(items_to_allocate)}")

    if not items_to_allocate:
        # Should be caught by the check above, but as a safeguard.
        return
        
    allocated_ids = tuple(item['id'] for item in items_to_allocate)

    # 3. Update the status of the specific items to 'sold' and link them to the order item.
    cursor.execute(
        """
        UPDATE product_items
        SET status = 'sold', order_item_id = %s
        WHERE id IN %s
        """,
        (order_item_id, allocated_ids)
    )
    logger.info(f"Allocated {len(allocated_ids)} items for order_item_id {order_item_id}")

def finalize_order(order_id):
    """Finalizes an order after successful payment."""
    logger.info(f"Processing 'finalize_order' job for order {order_id}")
    try:
        # 1. Update order status to 'Processing'.
        # 2. Decrement inventory for each item in the order.
        # 3. Award points to the user.
        # All within a single database transaction.

        # Queue subsequent jobs
        queue.enqueue('worker.send_email', {'type': 'orderConfirmation', 'orderId': order_id})
        queue.enqueue('worker.generate_invoice', order_id)
    except Exception as e:
        logger.error({'message': f"Job 'finalize_order' failed for order {order_id}", 'error': str(e)})
        raise # Re-raise to allow for retries

def send_email(email_details):
    """Sends an email via a third-party service."""
    recipient = email_details.get('recipient')
    logger.info(f"Sending email to {recipient}")
    try:
        # Integrate with an email service like SendGrid, Mailgun, etc.
        email_service.send(email_details)
    except Exception as e:
        logger.error({'message': f"Job 'send_email' failed for recipient {recipient}", 'error': str(e)})
        raise
