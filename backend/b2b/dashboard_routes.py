from flask import Blueprint, jsonify
from backend.auth.permissions import b2b_user_required
from flask_jwt_extended import get_jwt_identity
from backend.services.user_service import UserService
from backend.services.order_service import OrderService
from backend.models.user_models import User
from backend.models.b2b_models import B2BUser
from backend.models.order_models import Order, Invoice
from backend.models.enums import OrderStatus
from backend.database import db
from sqlalchemy import func, desc
from decimal import Decimal
from backend.auth.permissions import b2b_user_required
import json

dashboard_routes = Blueprint('b2b_dashboard_routes', __name__)


@b2b_dashboard_bp.route('/pro/dashboard', methods=['GET'])
@b2b_user_required
def get_b2b_dashboard_data():
    """
    Aggregates and returns key data points for the B2B user's dashboard.
    Implements caching to reduce database load for frequently accessed data.
    """
    user_id = get_jwt_identity()
    cache_key = f"b2b_dashboard:{user_id}"

    try:
        # 1. Attempt to fetch data from the cache first.
        cached_data = redis_client.get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for B2B dashboard, user_id: {user_id}")
            return jsonify(json.loads(cached_data)), 200
    except Exception as e:
        # If Redis is down, log the error but proceed to fetch from DB.
        logger.error(f"Redis cache read error for user {user_id}: {e}")

    logger.info(f"Cache miss for B2B dashboard, fetching from DB for user_id: {user_id}")

    # 2. If cache miss, connect to the database with robust error handling.
    try:
        conn = db.get_connection()
        cursor = conn.cursor(dictionary=True)
    except Exception as e:
        logger.critical(f"DATABASE CONNECTION FAILED for B2B dashboard: {e}")
        return jsonify({"error": "Could not connect to the database."}), 503 # Service Unavailable

    try:
        # 3. Execute several optimized, smaller queries instead of one large one.

        # Query for KPIs (Key Performance Indicators)
        cursor.execute(
            """
            SELECT
                COUNT(id) as total_orders,
                SUM(total) as total_spending
            FROM orders
            WHERE user_id = %s AND status IN ('delivered', 'shipped', 'processing')
            """,
            (user_id,)
        )
        kpis = cursor.fetchone()

        # Query for recent orders (e.g., last 5)
        cursor.execute(
            """
            SELECT id, total, status, created_at
            FROM orders
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 5
            """,
            (user_id,)
        )
        recent_orders = cursor.fetchall()

        # Query for pending invoice count
        cursor.execute(
            """
            SELECT COUNT(id) as pending_invoices
            FROM invoices
            WHERE user_id = %s AND deleted_at IS NULL
            """, # In a real system, you might also check a 'paid' status.
            (user_id,)
        )
        invoice_info = cursor.fetchone()

        # 4. Assemble the final dashboard data object.
        dashboard_data = {
            "kpis": {
                "total_orders": kpis.get('total_orders') or 0,
                "total_spending": float(kpis.get('total_spending') or 0.0),
                "pending_invoices": invoice_info.get('pending_invoices') or 0
            },
            "recent_orders": recent_orders
        }

        # 5. Store the result in the cache with an expiration time (e.g., 1 hour).
        try:
            redis_client.setex(cache_key, 3600, json.dumps(dashboard_data, default=str))
        except Exception as e:
            # Log cache write errors but don't fail the request.
            logger.error(f"Redis cache write error for user {user_id}: {e}")

        return jsonify(dashboard_data), 200

    except Exception as e:
        logger.error(f"Failed to fetch B2B dashboard data from DB for user {user_id}: {e}")
        return jsonify({"error": "An error occurred while fetching dashboard data."}), 500
    finally:
        # Ensure the connection is always closed.
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()



@dashboard_routes.route('/dashboard-summary', methods=['GET'])
@b2b_user_required
def get_b2b_dashboard_summary():
    """
    Get a lighter version of dashboard data for quick loading.
    Compatible with existing frontend code.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.b2b_account:
        return jsonify({"error": "B2B account not found"}), 404
    
    b2b_user = user.b2b_account[0]
    
    # Get basic stats
    recent_orders = Order.query.filter_by(user_id=user_id)\
        .order_by(desc(Order.created_at))\
        .limit(3)\
        .all()
    
    pending_invoices = db.session.query(Invoice, Order)\
        .join(Order, Invoice.order_id == Order.id)\
        .filter(Order.user_id == user_id)\
        .filter(Order.status == OrderStatus.COMPLETED)\
        .limit(2)\
        .all()
    
    summary_data = {
        "recent_orders": [order.to_dict() for order in recent_orders],
        "pending_invoices": [{
            "id": invoice.id,
            "amount": float(order.total_amount)
        } for invoice, order in pending_invoices],
        "loyalty_status": {
            "tier_name": b2b_user.tier.name if b2b_user.tier else "No Tier",
            "points": 0  # Implement if needed
        }
    }
    
    return jsonify(summary_data), 200
