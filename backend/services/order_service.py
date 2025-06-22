from backend.models.order_models import Order
from backend.database import db
from sqlalchemy import desc

class OrderService:
    @staticmethod
    def get_orders_by_user(user_id, limit=None):
        """Get orders for a specific user, optionally limited."""
        query = Order.query.filter_by(user_id=user_id).order_by(desc(Order.created_at))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_order_by_id(order_id, user_id=None):
        """Get a specific order, optionally filtered by user."""
        query = Order.query.filter_by(id=order_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.first()
    
    @staticmethod
    def create_order(user_id, order_data):
        """Create a new order."""
        order = Order(
            user_id=user_id,
            total_amount=order_data['total_amount'],
            status=order_data.get('status', 'PENDING')
        )
        db.session.add(order)
        db.session.commit()
        return order
    
    @staticmethod
    def update_order_status(order_id, new_status):
        """Update an order's status."""
        order = Order.query.get(order_id)
        if order:
            order.status = new_status
            db.session.commit()
        return order
