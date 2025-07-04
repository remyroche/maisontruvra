from datetime import datetime, timedelta

from sqlalchemy import func

from backend.database import db
from backend.models.order_models import Order
from backend.services.loyalty_service import LoyaltyService


class DashboardService:
    @staticmethod
    @staticmethod
    def get_dashboard_data(user_id, user_type):
        """Aggregates all necessary data for the B2C user dashboard."""
        user_loyalty = LoyaltyService.get_user_loyalty_status(user_id)
        recent_orders = OrderService.get_all_orders_for_user(
            user_id, user_type, limit=3
        )

        return {
            "loyaltyStatus": user_loyalty.to_dict() if user_loyalty else None,
            "recentOrders": [order.to_dict() for order in recent_orders],
        }

    def get_dashboard_stats(user_id: int) -> dict:
        """
        Aggregates and returns key statistics for a B2B user's dashboard.

        Args:
            user_id: The ID of the user.

        Returns:
            A dictionary containing dashboard statistics.
        """
        if not user_id:
            return {}

        # 1. Calculate Lifetime Spending
        # Assumes the Order model has a 'total' field for the order amount.
        lifetime_spending = (
            db.session.query(func.sum(Order.total))
            .filter(Order.user_id == user_id)
            .scalar()
            or 0.0
        )

        # 2. Count Recent Orders (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_orders_count = (
            db.session.query(func.count(Order.id))
            .filter(Order.user_id == user_id, Order.created_at >= thirty_days_ago)
            .scalar()
            or 0
        )

        # 3. Get Loyalty Information by calling the LoyaltyService
        # This demonstrates service-to-service communication.
        loyalty_status = LoyaltyService.get_user_loyalty_status(user_id)

        # 4. Combine all stats into a single response object
        stats = {
            "lifetimeSpending": lifetime_spending,
            "recentOrdersCount": recent_orders_count,
            "loyaltyPoints": loyalty_status.get("points", 0),
            "loyaltyTier": loyalty_status.get("tier", "Standard"),
        }

        return stats
