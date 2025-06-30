# FILE: routes/b2b_quick_order.py
# This Flask blueprint handles the B2B quick order functionality,
# allowing users to create an order directly from a list of SKUs.
# -----------------------------------------------------------------------------

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from backend.utils.decorators import b2b_user_required
from backend.utils.input_sanitizer import InputSanitizer
from backend.services.monitoring_service import MonitoringService
from flask import current_app
from backend.database import db
from redis import Redis
from rq import Queue

# Redis queue will be initialized in the function to avoid context issues

b2b_quick_order_bp = Blueprint('b2b_quick_order', __name__)

@b2b_quick_order_bp.route('/pro/quick-order', methods=['POST'])
@b2b_user_required
def create_b2b_quick_order():
    """
    Creates an order for a B2B user from a list of SKUs and quantities.
    This performs full SKU validation and inventory checks within a transaction.
    """
    user_id = get_jwt_identity()
    data = InputSanitizer.sanitize_input(request.get_json())
    items = data.get('items')

    if not items or not isinstance(items, list):
        return jsonify({"error": "A list of 'items' is required."}), 400

    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.begin()

        validated_items = []
        order_total = 0.0

        # --- Phase 1: Validation and Inventory Check ---
        for item in items:
            sku = item.get('sku')
            quantity = item.get('quantity')
            if not sku or not isinstance(quantity, int) or quantity <= 0:
                conn.rollback()
                return jsonify({"error": "Each item must have a valid SKU and a positive integer quantity."}), 400

            # Lock the variant row to prevent race conditions
            cursor.execute("SELECT id, price, inventory_count FROM product_variants WHERE sku = %s FOR UPDATE", (sku,))
            variant = cursor.fetchone()

            # SKU Validation
            if not variant:
                conn.rollback()
                return jsonify({"error": f"SKU not found: {sku}"}), 404

            # Inventory Check
            if variant['inventory_count'] < quantity:
                conn.rollback()
                return jsonify({"error": f"Insufficient stock for SKU {sku}. Available: {variant['inventory_count']}"}), 409

            item_total = float(variant['price']) * quantity
            order_total += item_total
            validated_items.append({
                "variant_id": variant['id'],
                "quantity": quantity,
                "price_at_purchase": variant['price']
            })

        # --- Phase 2: Order Creation and Inventory Update ---
        if not validated_items:
            return jsonify({"error": "No valid items to order."}), 400

        # Create the main order record. Assume a default 'processing' status.
        cursor.execute(
            "INSERT INTO orders (user_id, total, status) VALUES (%s, %s, 'processing')",
            (user_id, order_total)
        )
        order_id = cursor.lastrowid

        # Insert order items and update inventory
        for item in validated_items:
            # Insert the item into order_items
            cursor.execute(
                """INSERT INTO order_items (order_id, product_variant_id, quantity, price_at_purchase)
                   VALUES (%s, %s, %s, %s)""",
                (order_id, item['variant_id'], item['quantity'], item['price_at_purchase'])
            )
            # Decrement the inventory for the variant
            cursor.execute(
                "UPDATE product_variants SET inventory_count = inventory_count - %s WHERE id = %s",
                (item['quantity'], item['variant_id'])
            )

        conn.commit()

        # --- Phase 3: Post-Order Tasks (optional, can be done by a worker) ---
        # Queue a background job to allocate specific serialized items
        # and generate the invoice.
        redis_conn = Redis.from_url(current_app.config.get('REDIS_URL', 'redis://localhost:6379'))
        queue = Queue(connection=redis_conn)
        queue.enqueue('worker.fulfill_order', order_id)
        
        return jsonify({
            "message": "Quick order created successfully.",
            "order_id": order_id,
            "total": order_total
        }), 201

    except Exception as e:
        # Ensure rollback on any failure
        if 'conn' in locals() and conn.is_connected():
            conn.rollback()
        MonitoringService.log_error(f"B2B Quick Order failed for user {user_id}: {e}")
        return jsonify({"error": "An internal error occurred during order creation."}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
