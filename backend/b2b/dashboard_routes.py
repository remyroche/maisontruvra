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

dashboard_routes = Blueprint('b2b_dashboard_routes', __name__)

@dashboard_routes.route('/dashboard', methods=['GET'])
@b2b_user_required
def get_b2b_dashboard_data():
    """
    Get comprehensive dashboard data for the logged-in B2B user.
    Aggregates orders, invoices, loyalty status, and KPIs.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.b2b_account:
        return jsonify({"error": "B2B account not found"}), 404
    
    b2b_user = user.b2b_account[0]
    
    # Get recent orders (last 5)
    recent_orders = Order.query.filter_by(user_id=user_id)\
        .order_by(desc(Order.created_at))\
        .limit(5)\
        .all()
    
    # Calculate KPIs
    total_orders = Order.query.filter_by(user_id=user_id).count()
    
    completed_orders = Order.query.filter_by(
        user_id=user_id, 
        status=OrderStatus.COMPLETED
    ).all()
    
    total_spent = sum(float(order.total_amount) for order in completed_orders)
    average_order_value = total_spent / len(completed_orders) if completed_orders else 0
    
    # Get pending invoices
    pending_invoices = db.session.query(Invoice, Order)\
        .join(Order, Invoice.order_id == Order.id)\
        .filter(Order.user_id == user_id)\
        .filter(Order.status.in_([OrderStatus.COMPLETED, OrderStatus.SHIPPED]))\
        .order_by(desc(Invoice.created_at))\
        .limit(3)\
        .all()
    
    # Get loyalty information
    loyalty_data = {
        "tier": b2b_user.tier.name if b2b_user.tier else "No Tier",
        "tier_benefits": b2b_user.tier.benefits if b2b_user.tier else None,
        "points_balance": 0,  # Implement points system if needed
        "referral_code": getattr(user, 'referral_code', None)
    }
    
    # Get most purchased products (top 3)
    most_purchased_query = db.session.query(
        func.sum(db.text('order_items.quantity')).label('total_quantity'),
        db.text('products.name').label('product_name'),
        db.text('products.id').label('product_id')
    ).select_from(
        db.text('order_items')
    ).join(
        db.text('orders'), db.text('order_items.order_id = orders.id')
    ).join(
        db.text('products'), db.text('order_items.product_id = products.id')
    ).filter(
        db.text('orders.user_id = :user_id')
    ).filter(
        db.text('orders.status = :status')
    ).group_by(
        db.text('products.id'), db.text('products.name')
    ).order_by(
        db.text('total_quantity DESC')
    ).limit(3)
    
    most_purchased_products = db.session.execute(
        most_purchased_query, 
        {'user_id': user_id, 'status': OrderStatus.COMPLETED.value}
    ).fetchall()
    
    dashboard_data = {
        "company_name": b2b_user.company_name,
        "vat_number": b2b_user.vat_number,
        
        # KPIs
        "kpis": {
            "total_spent": total_spent,
            "total_orders": total_orders,
            "average_order_value": round(average_order_value, 2)
        },
        
        # Recent orders
        "recent_orders": [order.to_dict() for order in recent_orders],
        
        # Pending invoices
        "pending_invoices": [{
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "order_id": invoice.order_id,
            "total_amount": float(order.total_amount),
            "created_at": invoice.created_at.isoformat(),
            "status": order.status.value
        } for invoice, order in pending_invoices],
        
        # Loyalty status
        "loyalty_status": loyalty_data,
        
        # Most purchased products
        "most_purchased_products": [{
            "product_id": product.product_id,
            "product_name": product.product_name,
            "total_quantity": int(product.total_quantity)
        } for product in most_purchased_products],
        
        # Quick stats for the frontend
        "quick_stats": {
            "orders_this_month": Order.query.filter(
                Order.user_id == user_id,
                func.extract('month', Order.created_at) == func.extract('month', func.now()),
                func.extract('year', Order.created_at) == func.extract('year', func.now())
            ).count(),
            "pending_orders": Order.query.filter_by(
                user_id=user_id, 
                status=OrderStatus.PENDING
            ).count()
        }
    }
    
    return jsonify(dashboard_data), 200

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
