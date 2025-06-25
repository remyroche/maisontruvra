
from backend.database import db
from backend.models.user_models import User
from backend.models.b2b_loyalty_models import LoyaltyPointTransaction, LoyaltyTier
from backend.services.exceptions import ValidationError, NotFoundError
from sqlalchemy import func
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class LoyaltyService:
    @staticmethod
    def update_settings(settings_data: dict) -> dict:
        """
        Update loyalty program settings.
        """
        try:
            # Validate settings data
            required_fields = ['points_per_dollar', 'reward_threshold']
            for field in required_fields:
                if field not in settings_data:
                    raise ValidationError(f"Missing required field: {field}")
            
            # Update settings in database (assuming a settings table exists)
            # For now, return the validated data
            return {
                'points_per_dollar': float(settings_data['points_per_dollar']),
                'reward_threshold': int(settings_data['reward_threshold']),
                'updated_at': datetime.utcnow().isoformat()
            }
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid settings data: {str(e)}")

    @staticmethod
    def adjust_points(user_id: int, points: int, reason: str) -> int:
        """
        Manually adjust points for a user with audit logging.
        """
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")
        
        # Create point transaction record
        transaction = LoyaltyPointTransaction(
            user_id=user_id,
            points=points,
            transaction_type='manual_adjustment',
            description=f"Manual adjustment: {reason}",
            expires_at=datetime.utcnow() + timedelta(days=365),
            created_at=datetime.utcnow()
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        # Log the manual adjustment
        logger.info(f"Manual point adjustment: User {user_id}, Points {points}, Reason: {reason}")
        
        # Calculate new balance
        total_points = db.session.query(func.sum(LoyaltyPointTransaction.points)).filter(
            LoyaltyPointTransaction.user_id == user_id,
            LoyaltyPointTransaction.is_expired == False,
            LoyaltyPointTransaction.expires_at > datetime.utcnow()
        ).scalar() or 0
        
        return int(total_points)


from datetime import datetime, timedelta
from sqlalchemy import func, case
from backend.database import db
from backend.models.user_models import User
from backend.models.b2b_loyalty_models import LoyaltyPointTransaction, LoyaltyTier
from backend.services.referral_service import ReferralService

class LoyaltyService:

    @staticmethod
    def get_user_loyalty_status(user_id: int) -> dict | None:
        """
        Gets a user's current loyalty status, including valid points and tier.

        Args:
            user_id: The ID of the user to look up.

        Returns:
            A dictionary with the user's points, tier name, and referral code, or None if user not found.
        """
        user = User.query.get(user_id)
        if not user:
            return None

        # 1. Calculate the user's current valid (non-expired) point balance.
        # This sums up all point transactions that have not expired.
        valid_points = db.session.query(
            func.sum(LoyaltyPointTransaction.points)
        ).filter(
            LoyaltyPointTransaction.user_id == user_id,
            LoyaltyPointTransaction.is_expired == False,
            LoyaltyPointTransaction.expires_at > datetime.utcnow()
        ).scalar() or 0
        
        # 2. Get the user's tier name from the relationship.
        tier_name = user.loyalty_tier.name if user.loyalty_tier else 'Standard'

        # 3. Get the user's referral code.
        # Assuming the referral code is stored on the user model.
        referral_code = user.referral_code if hasattr(user, 'referral_code') else f"B2B-{user.id}-INCOMPLETE"

        return {
            'points': valid_points,
            'tier': tier_name,
            'referralCode': referral_code
        }

    @staticmethod
    def get_all_tier_discounts() -> list:
        """
        Gets the names and discount percentages for all loyalty tiers
        as configured by an administrator in the database.

        Returns:
            A list of dictionaries, e.g., [{'name': 'Partenaire', 'discount_percentage': 10.0}]
        """
        tiers = LoyaltyTier.query.order_by(LoyaltyTier.discount_percentage).all()
        
        # Serialize the data into the required format
        return [
            {
                "name": tier.name,
                "discount_percentage": tier.discount_percentage
            }
            for tier in tiers
        ]

    @staticmethod
    def add_points_for_purchase(user_id: int, order_total: float, order_id: int):
        """
        Awards points for a purchase and handles referral bonuses.
        Rule 1: 1 point per 1€ for the buyer, 0.1 for the referrer.
        """
        # Award points to the buyer
        points_to_award = int(order_total)
        if points_to_award > 0:
            buyer_transaction = LoyaltyPointTransaction(
                user_id=user_id,
                points=points_to_award,
                reason=f"Order #{order_id}",
                order_id=order_id
            )
            db.session.add(buyer_transaction)

        # Check for and award points to the referrer
        referrer = ReferralService.get_referrer_for_user(user_id)
        if referrer:
            referrer_points = int(order_total * 0.1)
            if referrer_points > 0:
                referrer_transaction = LoyaltyPointTransaction(
                    user_id=referrer.id,
                    points=referrer_points,
                    reason=f"Referral bonus from user #{user_id}'s order"
                )
                db.session.add(referrer_transaction)
        
        db.session.commit()

    @staticmethod
    def get_user_balance(user_id: int) -> int:
        """
        Calculates a user's current valid (non-expired) point balance.
        Rule 2: Points expire after 1 year.
        """
        balance = db.session.query(
            func.sum(LoyaltyPointTransaction.points)
        ).filter(
            LoyaltyPointTransaction.user_id == user_id,
            LoyaltyPointTransaction.is_expired == False,
            LoyaltyPointTransaction.expires_at > datetime.utcnow()
        ).scalar()
        return balance or 0

    @staticmethod
    def get_tier_and_discount(user_id: int) -> dict:
        """
        Gets the user's current tier and associated discount.
        Rule 4: Tier-based discounts.
        """
        user = User.query.get(user_id)
        if user and user.loyalty_tier:
            return {
                "tier": user.loyalty_tier.name,
                "discount_percentage": user.loyalty_tier.discount_percentage
            }
        return {"tier": "Standard", "discount_percentage": 0.0}

    @staticmethod
    def expire_points_task():
        """
        Scheduled Task: Marks all points older than 1 year as expired.
        This should be run daily by Celery.
        """
        expired_transactions = LoyaltyPointTransaction.query.filter(
            LoyaltyPointTransaction.expires_at <= datetime.utcnow(),
            LoyaltyPointTransaction.is_expired == False
        ).all()

        for trans in expired_transactions:
            trans.is_expired = True
        
        db.session.commit()
        return len(expired_transactions)


    @staticmethod
    def get_loyalty_tiers() -> list:
        """
        Retrieves all defined loyalty tiers.
        """
        tiers = LoyaltyTier.query.order_by(LoyaltyTier.min_points.asc()).all()
        return [tier.to_dict() for tier in tiers]

    @staticmethod
    def create_loyalty_tier(name: str, min_points: int, discount_percentage: float) -> LoyaltyTier:
        """
        Creates a new loyalty tier.
        """
        if LoyaltyTier.query.filter_by(name=name).first():
            raise ValidationError(f"Loyalty tier with name '{name}' already exists.")
        
        new_tier = LoyaltyTier(name=name, min_points=min_points, discount_percentage=discount_percentage)
        db.session.add(new_tier)
        db.session.commit()
        return new_tier

    @staticmethod
    def update_loyalty_tier(tier_id: int, name: str, min_points: int, discount_percentage: float) -> LoyaltyTier:
        """
        Updates an existing loyalty tier.
        """
        tier = LoyaltyTier.query.get(tier_id)
        if not tier:
            raise NotFoundError(f"Loyalty tier with ID {tier_id} not found.")
        
        # Check for duplicate name if name is changed
        if tier.name != name and LoyaltyTier.query.filter_by(name=name).first():
            raise ValidationError(f"Loyalty tier with name '{name}' already exists.")
            
        tier.name = name
        tier.min_points = min_points
        tier.discount_percentage = discount_percentage

    @staticmethod
    def update_user_tiers_task():
        """
        Scheduled Task: Recalculates and assigns loyalty tiers.
        This should be run daily by Celery.
        Rule 3: Tiers based on active users and point ranking.
        """
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        
        # 1. Get active B2B users and their valid point balances
        active_users_subquery = db.session.query(
            User.id.label('user_id'),
            func.sum(LoyaltyPointTransaction.points).label('total_points')
        ).join(LoyaltyPointTransaction, User.id == LoyaltyPointTransaction.user_id)\
         .filter(
            User.user_type == 'B2B', # Assuming a field to identify B2B users
            User.last_active_at >= three_months_ago,
            LoyaltyPointTransaction.is_expired == False,
            LoyaltyPointTransaction.expires_at > datetime.utcnow()
        ).group_by(User.id).subquery()

        # 2. Rank the active users by points
        ranked_users = db.session.query(
            active_users_subquery.c.user_id,
            active_users_subquery.c.total_points,
            func.rank().over(order_by=active_users_subquery.c.total_points.desc()).label('rank')
        ).all()

        # 3. Get total active users for tier calculation
        total_active_users = len(ranked_users)
        
        # 4. Calculate tier thresholds (top 10% Gold, next 20% Silver, rest Bronze)
        gold_threshold = max(1, int(total_active_users * 0.1))
        silver_threshold = max(1, int(total_active_users * 0.3))
        
        # 5. Get tier objects
        gold_tier = LoyaltyTier.query.filter_by(name='Gold').first()
        silver_tier = LoyaltyTier.query.filter_by(name='Silver').first()
        bronze_tier = LoyaltyTier.query.filter_by(name='Bronze').first()
        
        if not all([gold_tier, silver_tier, bronze_tier]):
            raise ValueError("Loyalty tiers not properly configured")
        
        # 6. Update user tiers
        updates_made = 0
        for ranked_user in ranked_users:
            user = User.query.get(ranked_user.user_id)
            if not user:
                continue
                
            new_tier = None
            if ranked_user.rank <= gold_threshold:
                new_tier = gold_tier
            elif ranked_user.rank <= silver_threshold:
                new_tier = silver_tier
            else:
                new_tier = bronze_tier
            
            if user.loyalty_tier_id != new_tier.id:
                user.loyalty_tier_id = new_tier.id
                updates_made += 1
        
        db.session.commit()
        return updates_made
