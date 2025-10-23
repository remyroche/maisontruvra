"""
Dashboard Service for providing real-time dashboard data.
"""

import logging
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload

from backend.database import db
from backend.models import Order, User, Product, Quote, NewsletterSubscription, POSTransaction

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for providing dashboard data."""
    
    def __init__(self, logger):
        self.logger = logger
    
    def get_dashboard_stats(self, days=30):
        """Get comprehensive dashboard statistics."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Sales statistics
            sales_stats = self._get_sales_stats(start_date, end_date)
            
            # User statistics
            user_stats = self._get_user_stats(start_date, end_date)
            
            # Product statistics
            product_stats = self._get_product_stats()
            
            # Quote statistics
            quote_stats = self._get_quote_stats(start_date, end_date)
            
            # Newsletter statistics
            newsletter_stats = self._get_newsletter_stats()
            
            # POS statistics
            pos_stats = self._get_pos_stats(start_date, end_date)
            
            return {
                "success": True,
                "data": {
                    "sales": sales_stats,
                    "users": user_stats,
                    "products": product_stats,
                    "quotes": quote_stats,
                    "newsletter": newsletter_stats,
                    "pos": pos_stats,
                    "period_days": days,
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_sales_stats(self, start_date, end_date):
        """Get sales statistics."""
        try:
            # Total revenue
            total_revenue = db.session.query(func.sum(Order.total_amount)).filter(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                Order.order_status.in_(['COMPLETED', 'DELIVERED'])
            ).scalar() or 0
            
            # Order count
            order_count = db.session.query(func.count(Order.id)).filter(
                Order.created_at >= start_date,
                Order.created_at <= end_date
            ).scalar() or 0
            
            # Completed orders
            completed_orders = db.session.query(func.count(Order.id)).filter(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                Order.order_status.in_(['COMPLETED', 'DELIVERED'])
            ).scalar() or 0
            
            # Average order value
            avg_order_value = total_revenue / completed_orders if completed_orders > 0 else 0
            
            # Daily sales trend
            daily_sales = db.session.query(
                func.date(Order.created_at).label('date'),
                func.sum(Order.total_amount).label('revenue'),
                func.count(Order.id).label('orders')
            ).filter(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                Order.order_status.in_(['COMPLETED', 'DELIVERED'])
            ).group_by(func.date(Order.created_at)).all()
            
            return {
                "total_revenue": float(total_revenue),
                "order_count": order_count,
                "completed_orders": completed_orders,
                "avg_order_value": float(avg_order_value),
                "daily_sales": [
                    {
                        "date": str(day.date),
                        "revenue": float(day.revenue or 0),
                        "orders": day.orders
                    }
                    for day in daily_sales
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting sales stats: {e}")
            return {}
    
    def _get_user_stats(self, start_date, end_date):
        """Get user statistics."""
        try:
            # Total users
            total_users = db.session.query(func.count(User.id)).scalar() or 0
            
            # New users in period
            new_users = db.session.query(func.count(User.id)).filter(
                User.created_at >= start_date,
                User.created_at <= end_date
            ).scalar() or 0
            
            # Active users (users with orders in period)
            active_users = db.session.query(func.count(func.distinct(Order.user_id))).filter(
                Order.created_at >= start_date,
                Order.created_at <= end_date
            ).scalar() or 0
            
            return {
                "total_users": total_users,
                "new_users": new_users,
                "active_users": active_users
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user stats: {e}")
            return {}
    
    def _get_product_stats(self):
        """Get product statistics."""
        try:
            # Total products
            total_products = db.session.query(func.count(Product.id)).scalar() or 0
            
            # Low stock products
            low_stock_products = db.session.query(func.count(Product.id)).filter(
                Product.stock <= 10
            ).scalar() or 0
            
            # Out of stock products
            out_of_stock_products = db.session.query(func.count(Product.id)).filter(
                Product.stock <= 0
            ).scalar() or 0
            
            return {
                "total_products": total_products,
                "low_stock_products": low_stock_products,
                "out_of_stock_products": out_of_stock_products
            }
            
        except Exception as e:
            self.logger.error(f"Error getting product stats: {e}")
            return {}
    
    def _get_quote_stats(self, start_date, end_date):
        """Get quote statistics."""
        try:
            # Total quotes
            total_quotes = db.session.query(func.count(Quote.id)).filter(
                Quote.created_at >= start_date,
                Quote.created_at <= end_date
            ).scalar() or 0
            
            # Pending quotes
            pending_quotes = db.session.query(func.count(Quote.id)).filter(
                Quote.created_at >= start_date,
                Quote.created_at <= end_date,
                Quote.status == 'pending'
            ).scalar() or 0
            
            # Responded quotes
            responded_quotes = db.session.query(func.count(Quote.id)).filter(
                Quote.created_at >= start_date,
                Quote.created_at <= end_date,
                Quote.status == 'responded'
            ).scalar() or 0
            
            return {
                "total_quotes": total_quotes,
                "pending_quotes": pending_quotes,
                "responded_quotes": responded_quotes
            }
            
        except Exception as e:
            self.logger.error(f"Error getting quote stats: {e}")
            return {}
    
    def _get_newsletter_stats(self):
        """Get newsletter statistics."""
        try:
            # Total subscribers
            total_subscribers = db.session.query(func.count(NewsletterSubscription.id)).filter(
                NewsletterSubscription.is_active == True
            ).scalar() or 0
            
            # B2C subscribers
            b2c_subscribers = db.session.query(func.count(NewsletterSubscription.id)).filter(
                NewsletterSubscription.is_active == True,
                NewsletterSubscription.list_type == 'b2c'
            ).scalar() or 0
            
            # B2B subscribers
            b2b_subscribers = db.session.query(func.count(NewsletterSubscription.id)).filter(
                NewsletterSubscription.is_active == True,
                NewsletterSubscription.list_type == 'b2b'
            ).scalar() or 0
            
            return {
                "total_subscribers": total_subscribers,
                "b2c_subscribers": b2c_subscribers,
                "b2b_subscribers": b2b_subscribers
            }
            
        except Exception as e:
            self.logger.error(f"Error getting newsletter stats: {e}")
            return {}
    
    def _get_pos_stats(self, start_date, end_date):
        """Get POS transaction statistics."""
        try:
            # Total POS transactions
            total_transactions = db.session.query(func.count(POSTransaction.id)).filter(
                POSTransaction.created_at >= start_date,
                POSTransaction.created_at <= end_date
            ).scalar() or 0
            
            # Completed transactions
            completed_transactions = db.session.query(func.count(POSTransaction.id)).filter(
                POSTransaction.created_at >= start_date,
                POSTransaction.created_at <= end_date,
                POSTransaction.status == 'completed'
            ).scalar() or 0
            
            # Total POS revenue
            pos_revenue = db.session.query(func.sum(POSTransaction.total_amount)).filter(
                POSTransaction.created_at >= start_date,
                POSTransaction.created_at <= end_date,
                POSTransaction.status == 'completed'
            ).scalar() or 0
            
            return {
                "total_transactions": total_transactions,
                "completed_transactions": completed_transactions,
                "total_revenue": float(pos_revenue)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting POS stats: {e}")
            return {}
    
    def get_recent_orders(self, limit=10):
        """Get recent orders for dashboard."""
        try:
            orders = db.session.query(Order).options(
                joinedload(Order.user),
                joinedload(Order.items)
            ).order_by(desc(Order.created_at)).limit(limit).all()
            
            return [
                {
                    "id": str(order.id),
                    "user_name": order.user.full_name if order.user else "Guest",
                    "user_email": order.user.email if order.user else order.guest_email,
                    "total_amount": float(order.total_amount),
                    "status": order.order_status.value,
                    "created_at": order.created_at.isoformat(),
                    "item_count": len(order.items)
                }
                for order in orders
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting recent orders: {e}")
            return []