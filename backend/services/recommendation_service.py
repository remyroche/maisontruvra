# backend/services/recommendation_service.py

from sqlalchemy import func

from ..models import Order, OrderItem, Product, User, db
from ..services.exceptions import NotFoundException, ServiceError
from ..services.monitoring_service import MonitoringService
from ..utils.input_sanitizer import InputSanitizer


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
            purchased_categories = (
                db.session.query(
                    Product.category_id,
                    func.count(Product.category_id).label("purchase_count"),
                )
                .join(OrderItem, OrderItem.product_id == Product.id)
                .join(Order, Order.id == OrderItem.order_id)
                .filter(Order.user_id == safe_user_id)
                .group_by(Product.category_id)
                .order_by(func.count(Product.category_id).desc())
                .all()
            )

            if not purchased_categories:
                # Fallback: If user has no purchase history, recommend general best-sellers or new arrivals
                return RecommendationService.get_general_recommendations(limit)

            # Get a list of all products the user has already bought
            purchased_product_ids = [
                p.product_id
                for p in db.session.query(OrderItem.product_id)
                .join(Order)
                .filter(Order.user_id == safe_user_id)
                .all()
            ]

            recommended_products = []
            category_ids = [c.category_id for c in purchased_categories]

            # Find products in the preferred categories that the user hasn't bought
            recommended_products = (
                Product.query.filter(
                    Product.category_id.in_(category_ids),
                    ~Product.id.in_(purchased_product_ids),
                )
                .limit(limit)
                .all()
            )

            # If not enough recommendations, fill with general ones
            if len(recommended_products) < limit:
                general_recs = RecommendationService.get_general_recommendations(
                    limit - len(recommended_products),
                    exclude_ids=purchased_product_ids
                    + [p.id for p in recommended_products],
                )
                recommended_products.extend(general_recs)

            return [p.to_dict() for p in recommended_products]

        except Exception as e:
            MonitoringService.log_error(
                f"Error generating recommendations for user {user_id}: {str(e)}",
                "RecommendationService",
                exc_info=True,
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
        best_sellers_query = (
            db.session.query(
                Product, func.count(OrderItem.product_id).label("order_count")
            )
            .join(OrderItem, OrderItem.product_id == Product.id)
            .filter(~Product.id.in_(exclude_ids))
            .group_by(Product.id)
            .order_by(func.count(OrderItem.product_id).desc())
            .limit(limit)
        )

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
        recommendations = RecommendationService.get_recommendations_for_user(
            user_id, limit
        )

        # Add user context for admin view
        return {
            "user_id": user_id,
            "user_email": user.email,
            "user_name": f"{user.first_name} {user.last_name}".strip(),
            "recommendations": recommendations,
            "recommendation_count": len(recommendations),
        }

    @staticmethod
    def get_all_customer_recommendations(limit_per_user=5, page=1, per_page=50):
        """
        Get recommendations for all customers with pagination.
        This is for admin bulk view operations.
        """
        try:
            # Get all active users with pagination
            users_query = User.query.filter(User.is_active)
            total_users = users_query.count()

            users = users_query.offset((page - 1) * per_page).limit(per_page).all()

            all_recommendations = []

            for user in users:
                try:
                    user_recommendations = (
                        RecommendationService.get_recommendations_for_user(
                            user.id, limit_per_user
                        )
                    )

                    all_recommendations.append(
                        {
                            "user_id": user.id,
                            "user_email": user.email,
                            "user_name": f"{user.first_name} {user.last_name}".strip(),
                            "registration_date": user.created_at.isoformat()
                            if user.created_at
                            else None,
                            "last_login": user.last_login.isoformat()
                            if hasattr(user, "last_login") and user.last_login
                            else None,
                            "recommendations": user_recommendations,
                            "recommendation_count": len(user_recommendations),
                        }
                    )
                except Exception as e:
                    # Log error but continue with other users
                    MonitoringService.log_error(
                        f"Error generating recommendations for user {user.id}: {str(e)}",
                        "RecommendationService",
                        exc_info=True,
                    )
                    all_recommendations.append(
                        {
                            "user_id": user.id,
                            "user_email": user.email,
                            "user_name": f"{user.first_name} {user.last_name}".strip(),
                            "registration_date": user.created_at.isoformat()
                            if user.created_at
                            else None,
                            "last_login": user.last_login.isoformat()
                            if hasattr(user, "last_login") and user.last_login
                            else None,
                            "recommendations": [],
                            "recommendation_count": 0,
                            "error": "Failed to generate recommendations",
                        }
                    )

            return {
                "recommendations": all_recommendations,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total_users": total_users,
                    "total_pages": (total_users + per_page - 1) // per_page,
                    "has_next": page * per_page < total_users,
                    "has_prev": page > 1,
                },
            }

        except Exception as e:
            MonitoringService.log_error(
                f"Error generating bulk recommendations: {str(e)}",
                "RecommendationService",
                exc_info=True,
            )
            raise ServiceError(f"Failed to generate bulk recommendations: {str(e)}")

    @staticmethod
    def get_recommendations_summary():
        """
        Get a summary of recommendation statistics for admin dashboard.
        """
        try:
            # Get total active users
            total_users = User.query.filter(User.is_active).count()

            # Get users with purchase history (who would get personalized recommendations)
            users_with_orders = (
                db.session.query(User.id)
                .join(Order)
                .filter(User.is_active)
                .distinct()
                .count()
            )

            # Get users without purchase history (who would get general recommendations)
            users_without_orders = total_users - users_with_orders

            # Get most popular categories from recent orders
            popular_categories = (
                db.session.query(
                    Product.category_id, func.count(OrderItem.id).label("order_count")
                )
                .join(OrderItem, OrderItem.product_id == Product.id)
                .join(Order, Order.id == OrderItem.order_id)
                .group_by(Product.category_id)
                .order_by(func.count(OrderItem.id).desc())
                .limit(5)
                .all()
            )

            return {
                "total_active_users": total_users,
                "users_with_personalized_recommendations": users_with_orders,
                "users_with_general_recommendations": users_without_orders,
                "popular_categories": [
                    {"category_id": cat.category_id, "order_count": cat.order_count}
                    for cat in popular_categories
                ],
            }

        except Exception as e:
            MonitoringService.log_error(
                f"Error generating recommendations summary: {str(e)}",
                "RecommendationService",
                exc_info=True,
            )
            raise ServiceError(f"Failed to generate recommendations summary: {str(e)}")

    @staticmethod
    def bulk_generate_recommendations(user_ids, limit_per_user=5):
        """
        Generate recommendations for multiple users at once.
        Useful for bulk operations like email campaigns.
        """
        try:
            results = []

            for user_id in user_ids:
                try:
                    user_recommendations = (
                        RecommendationService.get_admin_recommendations_for_user(
                            user_id, limit_per_user
                        )
                    )
                    results.append(
                        {
                            "user_id": user_id,
                            "status": "success",
                            "data": user_recommendations,
                        }
                    )
                except NotFoundException:
                    results.append(
                        {
                            "user_id": user_id,
                            "status": "error",
                            "error": "User not found",
                        }
                    )
                except Exception as e:
                    results.append(
                        {"user_id": user_id, "status": "error", "error": str(e)}
                    )

            return {
                "results": results,
                "total_processed": len(user_ids),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "error"]),
            }

        except Exception as e:
            MonitoringService.log_error(
                f"Error in bulk recommendation generation: {str(e)}",
                "RecommendationService",
                exc_info=True,
            )
            raise ServiceError(f"Failed to generate bulk recommendations: {str(e)}")
