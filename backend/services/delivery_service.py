"""
Service layer for managing delivery methods, including caching and audit logging.
"""

from .. import db
from ..extensions import cache
from ..models.delivery_models import DeliveryMethod
from ..models.b2b_loyalty_models import LoyaltyTier
from ..models.user_models import User
from ..utils.input_sanitizer import InputSanitizer
from .audit_log_service import AuditLogService
from ..utils.cache_helpers import get_delivery_methods_key, clear_delivery_methods_cache


class DeliveryService:
    """
    Manages all operations related to delivery methods, including fetching,
    creation, updates, and deletion, with appropriate caching and logging.
    """

    @staticmethod
    def get_all_methods_for_admin():
        """
        Retrieves all delivery methods for the admin panel, including
        which tiers are associated with each. This method bypasses the cache
        to ensure admins see the most up-to-date information.
        """
        methods = DeliveryMethod.query.all()
        return [method.to_dict(include_tiers=True) for method in methods]

    @staticmethod
    def get_active_methods_cached():
        """
        Retrieves all *active* delivery methods, using a cache.
        This is ideal for public-facing parts of the site where performance
        is key and data changes infrequently.
        """
        cache_key = get_delivery_methods_key()
        methods = cache.get(cache_key)
        if methods is None:
            methods = (
                DeliveryMethod.query.filter_by(is_active=True)
                .order_by(DeliveryMethod.price)
                .all()
            )
            # Cache for 24 hours as this data is not expected to change often.
            cache.set(cache_key, methods, timeout=86400)
        return methods

    @staticmethod
    def get_available_methods_for_user(user_id: int):
        """
        Retrieves delivery methods available to a specific user based on their loyalty tier.
        """
        user = User.query.get(user_id)
        if not user or not user.loyalty_tier:
            # Fallback for users with no tier: find methods available to "Collaborateur"
            default_tier = LoyaltyTier.query.filter_by(name="Collaborateur").first()
            if not default_tier:
                return []
            # Note: This relationship relies on the back-reference from the tier model.
            return [
                method.to_dict()
                for method in default_tier.delivery_methods
                if method.is_active
            ]

        return [
            method.to_dict()
            for method in user.loyalty_tier.delivery_methods
            if method.is_active
        ]

    @staticmethod
    def create_method(data: dict):
        """
        Creates a new delivery method, logs the action, and clears the cache.
        """
        sanitized_data = InputSanitizer.sanitize_input(data)
        new_method = DeliveryMethod(
            name=sanitized_data["name"],
            description=sanitized_data.get("description", ""),
            price=float(sanitized_data["price"]),
            is_active=sanitized_data.get("is_active", True),
        )
        tier_ids = data.get("tier_ids", [])
        if tier_ids:
            accessible_tiers = LoyaltyTier.query.filter(
                LoyaltyTier.id.in_(tier_ids)
            ).all()
            new_method.accessible_to_tiers.extend(accessible_tiers)

        db.session.add(new_method)
        db.session.flush()  # Flush to get the ID for logging

        # --- AUDIT LOGGING ---
        AuditLogService.log_action(
            action="DELIVERY_METHOD_CREATE",
            target_id=new_method.id,
            details=new_method.to_dict(include_tiers=True),
        )

        db.session.commit()
        clear_delivery_methods_cache()  # Invalidate cache on create
        return new_method

    @staticmethod
    def update_method(method_id: int, data: dict):
        """
        Updates an existing delivery method, logs the changes, and clears the cache.
        """
        method = DeliveryMethod.query.get_or_404(method_id)
        old_details = method.to_dict(include_tiers=True)  # Capture state before changes

        sanitized_data = InputSanitizer.sanitize_input(data)
        method.name = sanitized_data.get("name", method.name)
        method.description = sanitized_data.get("description", method.description)
        method.price = float(sanitized_data.get("price", method.price))
        method.is_active = sanitized_data.get("is_active", method.is_active)

        if "tier_ids" in data:
            method.accessible_to_tiers.clear()
            tier_ids = data.get("tier_ids", [])
            if tier_ids:
                accessible_tiers = LoyaltyTier.query.filter(
                    LoyaltyTier.id.in_(tier_ids)
                ).all()
                method.accessible_to_tiers.extend(accessible_tiers)

        new_details = method.to_dict(include_tiers=True)  # Capture state after changes

        # --- AUDIT LOGGING ---
        AuditLogService.log_action(
            action="DELIVERY_METHOD_UPDATE",
            target_id=method.id,
            details={"before": old_details, "after": new_details},
        )

        db.session.commit()
        clear_delivery_methods_cache()  # Invalidate cache on update
        return method

    @staticmethod
    def delete_method(method_id: int):
        """Deletes a delivery method, logs the action, and clears the cache."""
        method = DeliveryMethod.query.get_or_404(method_id)
        method_details = method.to_dict(
            include_tiers=True
        )  # Get details before deleting

        db.session.delete(method)

        # --- AUDIT LOGGING ---
        AuditLogService.log_action(
            action="DELIVERY_METHOD_DELETE", target_id=method_id, details=method_details
        )

        db.session.commit()
        clear_delivery_methods_cache()  # Invalidate cache on delete
        return True
