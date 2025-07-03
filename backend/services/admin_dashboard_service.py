from datetime import datetime, timedelta
from sqlalchemy import func
from backend.database import db
from backend.models.order_models import Order, OrderStatusEnum
from backend.models.user_models import User
from backend.models.product_models import Product, Review

class AdminDashboardService:
    """
    Service containing the business logic for the main administrative dashboard.
    """

    @staticmethod
    def get_platform_stats() -> dict:
        """
        Calculates and returns the key performance indicators (KPIs) for the
        entire platform.
        """
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        # 1. Calculate Total Revenue from all completed orders
        total_revenue = db.session.query(
            func.sum(Order.total)
        ).filter(
            Order.status == OrderStatusEnum.COMPLETED
        ).scalar() or 0.0

        # 2. Count New Customers registered in the last 30 days
        new_customers_count = db.session.query(
            func.count(User.id)
        ).filter(
            User.created_at >= thirty_days_ago
        ).scalar() or 0

        # 3. Count Orders with a 'pending' status
        pending_orders_count = db.session.query(
            func.count(Order.id)
        ).filter(
            Order.status == OrderStatusEnum.PENDING
        ).scalar() or 0

        # 4. Count the total number of products in the catalog
        total_products_count = db.session.query(
            func.count(Product.id)
        ).scalar() or 0

        return {
            "totalRevenue": total_revenue,
            "newCustomersCount": new_customers_count,
            "pendingOrdersCount": pending_orders_count,
            "totalProductsCount": total_products_count,
        }

    @staticmethod
    def get_recent_activity(limit: int = 10) -> list:
        """
        Fetches and combines a list of the most recent significant activities
        from across the platform.
        """
        recent_activities = []

        # Fetch recent orders
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(limit).all()
        for order in recent_orders:
            recent_activities.append({
                "type": "Nouvelle Commande",
                "timestamp": order.created_at,
                "description": f"Commande n°{order.id} d'un montant de {order.total:.2f}€",
                "user": order.user.email if order.user else "Utilisateur anonyme",
                "link": f"/admin/manage_orders.html?orderId={order.id}" # Example link
            })

        # Fetch recent user registrations
        recent_users = User.query.order_by(User.created_at.desc()).limit(limit).all()
        for user in recent_users:
            recent_activities.append({
                "type": "Nouvel Utilisateur",
                "timestamp": user.created_at,
                "description": f"Inscription de {user.email}",
                "user": user.email,
                "link": f"/admin/manage_users.html?userId={user.id}" # Example link
            })
        
        # Fetch recent reviews
        recent_reviews = Review.query.order_by(Review.created_at.desc()).limit(limit).all()
        for review in recent_reviews:
             recent_activities.append({
                "type": "Nouvel Avis",
                "timestamp": review.created_at,
                "description": f"Avis de {review.rating} étoiles pour le produit '{review.product.name}'",
                "user": review.user.email if review.user else "Utilisateur anonyme",
                "link": f"/admin/manage_reviews.html?reviewId={review.id}" # Example link
            })


        # Sort all activities by timestamp descending and take the most recent 'limit'
        recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Serialize the final list
        return [
            {
                "type": act["type"],
                "timestamp": act["timestamp"].isoformat(),
                "description": act["description"],
                "user": act["user"],
                "link": act["link"]
            } for act in recent_activities[:limit]
        ]
