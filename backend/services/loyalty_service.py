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

        total_ranked_users = len(ranked_users)
        if total_ranked_users == 0:
            return 0
        
        # 3. Get tier definitions from the database
        tiers = {tier.name: tier.id for tier in LoyaltyTier.query.all()}
        tier1_id = tiers.get('Tier 1')
        tier2_id = tiers.get('Tier 2')
        standard_tier_id = tiers.get('Standard')

        if not all([tier1_id, tier2_id, standard_tier_id]):
            raise Exception("Tier 1, Tier 2, and Standard tiers must be defined in the database.")

        # 4. Assign tiers based on percentile rank
        tier1_cutoff = total_ranked_users * 0.25
        tier2_cutoff = total_ranked_users * 0.50

        case_statement = case(
            (ranked_users.c.rank <= tier1_cutoff, tier1_id),
            (ranked_users.c.rank <= tier2_cutoff, tier2_id),
            else_=standard_tier_id
        )

        # 5. Update all users in a single bulk update
        db.session.query(User).filter(User.id.in_([u.user_id for u in ranked_users])).update({
            User.loyalty_tier_id: case_statement
        }, synchronize_session=False)

        db.session.commit()
        return total_ranked_users

