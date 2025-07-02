# backend/services/recommendation_service.py

from ..models import Product, User, Order, OrderItem, db
from ..services.monitoring_service import MonitoringService
from ..services.exceptions import NotFoundException, ServiceError
from ..utils.input_sanitizer import InputSanitizer
from sqlalchemy import func

class RecommendationService:
    """
    Handles business logic for generating product recommendations.
    """

    @staticmethod
    def get_recommendations_for_user(user_id, limit=5):
        """
        Generates product recommendations for a user based on their purchase history.
        
        A simple initial algorithm:
        1. Find all categories of products the user has purchased.
        2. Find other products in those categories that the user has NOT purchased.
        3. Prioritize products from the most frequently purchased categories.
        4. As a fallback, recommend best-selling products.
        """
        try:
            safe_user_id = InputSanitizer.sanitize_integer(user_id)
            
            # Find categories the user has purchased from
            purchased_categories = db.session.query(
                Product.category_id, func.count(Product.category_id).label('purchase_count')
            ).join(OrderItem, OrderItem.product_id == Product.id)\
             .join(Order, Order.id == OrderItem.order_id)\
             .filter(Order.user_id == safe_user_id)\
             .group_by(Product.category_id)\
             .order_by(func.count(Product.category_id).desc())\
             .all()

            if not purchased_categories:
                # Fallback: If user has no purchase history, recommend general best-sellers or new arrivals
                return RecommendationService.get_general_recommendations(limit)

            # Get a list of all products the user has already bought
            purchased_product_ids = [
                p.product_id for p in db.session.query(OrderItem.product_id).join(Order).filter(Order.user_id == safe_user_id).all()
            ]

            recommended_products = []
            category_ids = [c.category_id for c in purchased_categories]

            # Find products in the preferred categories that the user hasn't bought
            recommended_products = Product.query.filter(
                Product.category_id.in_(category_ids),
                ~Product.id.in_(purchased_product_ids)
            ).limit(limit).all()

            # If not enough recommendations, fill with general ones
            if len(recommended_products) < limit:
                general_recs = RecommendationService.get_general_recommendations(
                    limit - len(recommended_products),
                    exclude_ids=purchased_product_ids + [p.id for p in recommended_products]
                )
                recommended_products.extend(general_recs)

            return [p.to_dict() for p in recommended_products]

        except Exception as e:
            MonitoringService.log_error(
                f"Error generating recommendations for user {user_id}: {str(e)}",
                "RecommendationService",
                exc_info=True
            )
            raise ServiceError(f"Failed to generate recommendations: {str(e)}")

    @staticmethod
    def get_general_recommendations(limit=5, exclude_ids=None):
        """
        Fallback method to get general recommendations (e.g., best-sellers).
        """
        if exclude_ids is None:
            exclude_ids = []
            
        # Simple "best-seller" logic: products that appear most in orders
        best_sellers_query = db.session.query(
            Product, func.count(OrderItem.product_id).label('order_count')
        ).join(OrderItem, OrderItem.product_id == Product.id)\
         .filter(~Product.id.in_(exclude_ids))\
         .group_by(Product.id)\
         .order_by(func.count(OrderItem.product_id).desc())\
         .limit(limit)
        
        return [product for product, count in best_sellers_query.all()]

    @staticmethod
    def get_admin_recommendations_for_user(user_id, limit=5):
        """
        A method for admins to see what a user would be recommended.
        This is useful for personalizing marketing emails.
        """
        user = User.query.get(user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found.")
        
        # The logic is the same, just called from an admin context
        return RecommendationService.get_recommendations_for_user(user_id, limit)

