# backend/services/loyalty_service.py

from .. import db
from ..models import (User, LoyaltyProgram, LoyaltyTier, UserLoyalty, 
                      PointVoucher, ExclusiveReward, LoyaltyPointLog, 
                      Discount, DiscountType, Referral, ReferralRewardTier)
from ..models.loyalty_account import LoyaltyAccount
from sqlalchemy.exc import IntegrityError
import uuid

class LoyaltyService:
    """
    A unified service for managing the B2B loyalty program,
    including tiers, points, and rewards.
    """

    def __init__(self):
        pass

    # --- Loyalty Tier Management ---

    def get_all_tiers(self):
        """Retrieves all loyalty tiers from the database."""
        return LoyaltyTier.query.order_by(LoyaltyTier.points_required).all()

    def create_tier(self, data):
        """
        Creates a new loyalty tier.

        Args:
            data (dict): A dictionary containing tier details 
                         (name, points_required, description).

        Returns:
            A tuple of (LoyaltyTier|None, error_message|None).
        """
        name = data.get('name')
        points_required = data.get('points_required')
        description = data.get('description')

        if not all([name, points_required]):
            return None, "Missing required fields: name and points_required."

        try:
            new_tier = LoyaltyTier(
                name=name,
                points_required=points_required,
                description=description
            )
            db.session.add(new_tier)
            db.session.commit()
            return new_tier, None
        except IntegrityError:
            db.session.rollback()
            return None, "A tier with this name or points requirement already exists."
        except Exception as e:
            db.session.rollback()
            return None, f"An unexpected error occurred: {str(e)}"

    def update_tier(self, tier_id, data):
        """
        Updates an existing loyalty tier.

        Args:
            tier_id (uuid): The ID of the tier to update.
            data (dict): A dictionary containing the fields to update.

        Returns:
            A tuple of (LoyaltyTier|None, error_message|None).
        """
        tier = LoyaltyTier.query.get(tier_id)
        if not tier:
            return None, "Loyalty tier not found."

        try:
            for key, value in data.items():
                if hasattr(tier, key):
                    setattr(tier, key, value)
            db.session.commit()
            return tier, None
        except Exception as e:
            db.session.rollback()
            return None, f"An unexpected error occurred: {str(e)}"

    def delete_tier(self, tier_id):
        """
        Deletes a loyalty tier.

        Args:
            tier_id (uuid): The ID of the tier to delete.

        Returns:
            A tuple of (success_boolean, message).
        """
        tier = LoyaltyTier.query.get(tier_id)
        if not tier:
            return False, "Loyalty tier not found."

        try:
            db.session.delete(tier)
            db.session.commit()
            return True, "Loyalty tier deleted successfully."
        except Exception as e:
            db.session.rollback()
            return False, f"An unexpected error occurred: {str(e)}"

    # --- User Loyalty Management ---

    def get_user_loyalty_status(self, user_id):
        """
        Retrieves the loyalty status for a specific user.

        Args:
            user_id (uuid): The ID of the user.

        Returns:
            The UserLoyalty object or None if not found.
        """
        return UserLoyalty.query.filter_by(user_id=user_id).first()

    def add_loyalty_points(self, user_id, points, reason):
        """
        Adds loyalty points to a user's account and logs the transaction.

        Args:
            user_id (uuid): The user's ID.
            points (int): The number of points to add.
            reason (str): The reason for the points addition.

        Returns:
            A tuple of (LoyaltyAccount|None, error_message|None).
        """
        account = LoyaltyAccount.query.filter_by(user_id=user_id).first()
        if not account:
            return None, "User's loyalty account not found."

        try:
            account.points_balance += points
            
            # Log the transaction
            log_entry = LoyaltyPointLog(
                user_id=user_id,
                points_change=points,
                reason=reason
            )
            db.session.add(log_entry)
            
            # Check for tier update
            self.update_user_tier(user_id, account.points_balance)
            
            db.session.commit()
            return account, None
        except Exception as e:
            db.session.rollback()
            return None, f"Failed to add points: {str(e)}"

    def update_user_tier(self, user_id, current_points):
        """
        Updates a user's loyalty tier based on their points balance.
        This is typically called internally after a points change.
        """
        user_loyalty = UserLoyalty.query.filter_by(user_id=user_id).first()
        if not user_loyalty:
            return # Or handle error appropriately

        # Find the highest tier the user qualifies for
        eligible_tiers = LoyaltyTier.query.filter(
            LoyaltyTier.points_required <= current_points
        ).order_by(LoyaltyTier.points_required.desc()).all()

        if eligible_tiers:
            new_tier = eligible_tiers[0]
            if user_loyalty.tier_id != new_tier.id:
                user_loyalty.tier_id = new_tier.id
                # db.session.commit() will be called by the parent function