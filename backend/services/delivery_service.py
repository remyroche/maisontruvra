from backend.database import db
from backend.models.delivery_models import DeliveryMethod
from backend.models.b2b_loyalty_models import LoyaltyTier
from backend.models.user_models import User
from backend.utils.sanitization import sanitize_input
from backend.services.audit_log_service import AuditLogService

class DeliveryService:
    @staticmethod
    def get_all_methods_for_admin():
        """
        Retrieves all delivery methods for the admin panel, including
        which tiers are associated with each.
        """
        methods = DeliveryMethod.query.all()
        return [method.to_dict() for method in methods]

    @staticmethod
    def get_available_methods_for_user(user_id: int):
        """
        Retrieves delivery methods available to a specific user based on their loyalty tier.
        """
        user = User.query.get(user_id)
        if not user or not user.loyalty_tier:
            # Fallback for users with no tier: find methods available to "Collaborateur"
            default_tier = LoyaltyTier.query.filter_by(name='Collaborateur').first()
            if not default_tier:
                return []
            return [method.to_dict() for method in default_tier.delivery_methods]
        
        return [method.to_dict() for method in user.loyalty_tier.delivery_methods]
        
    @staticmethod
    def create_method(data: dict):
        """
        Creates a new delivery method and logs the action.
        """
        sanitized_data = sanitize_input(data)
        new_method = DeliveryMethod(
            name=sanitized_data['name'],
            description=sanitized_data.get('description', ''),
            price=float(sanitized_data['price'])
        )
        tier_ids = data.get('tier_ids', [])
        if tier_ids:
            accessible_tiers = LoyaltyTier.query.filter(LoyaltyTier.id.in_(tier_ids)).all()
            new_method.accessible_to_tiers.extend(accessible_tiers)
            
        db.session.add(new_method)
        db.session.flush() # Flush to get the ID for logging

        # --- AUDIT LOGGING ---
        AuditLogService.log_action(
            action='DELIVERY_METHOD_CREATE',
            target_id=new_method.id,
            details=new_method.to_dict()
        )
        
        db.session.commit()
        return new_method

    @staticmethod
    def update_method(method_id: int, data: dict):
        """
        Updates an existing delivery method and logs the changes.
        """
        method = DeliveryMethod.query.get_or_404(method_id)
        old_details = method.to_dict() # Capture state before changes
        
        sanitized_data = sanitize_input(data)
        method.name = sanitized_data.get('name', method.name)
        method.description = sanitized_data.get('description', method.description)
        method.price = float(sanitized_data.get('price', method.price))
        
        if 'tier_ids' in data:
            method.accessible_to_tiers.clear()
            tier_ids = data.get('tier_ids', [])
            if tier_ids:
                accessible_tiers = LoyaltyTier.query.filter(LoyaltyTier.id.in_(tier_ids)).all()
                method.accessible_to_tiers.extend(accessible_tiers)

        new_details = method.to_dict() # Capture state after changes

        # --- AUDIT LOGGING ---
        AuditLogService.log_action(
            action='DELIVERY_METHOD_UPDATE',
            target_id=method.id,
            details={'before': old_details, 'after': new_details}
        )
        
        db.session.commit()
        return method
        
    @staticmethod
    def delete_method(method_id: int):
        """Deletes a delivery method and logs the action."""
        method = DeliveryMethod.query.get_or_404(method_id)
        method_details = method.to_dict() # Get details before deleting
        
        db.session.delete(method)
        
        # --- AUDIT LOGGING ---
        AuditLogService.log_action(
            action='DELIVERY_METHOD_DELETE',
            target_id=method_id,
            details=method_details
        )
        
        db.session.commit()
        return True
