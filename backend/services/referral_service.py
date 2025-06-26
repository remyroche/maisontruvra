from backend.models.b2b_models import B2BUser
from backend.models.referral_models import Referral, ReferralReward
from backend.services.loyalty_service import LoyaltyService
from backend.database import db
from datetime import datetime, timedelta

class ReferralService:
    def __init__(self, session):
        self.session = session
        self.loyalty_service = LoyaltyService(session)

    def create_referral_link(self, referrer_id, referee_id):
        """
        Creates a permanent link between a referrer and a referee
        without any initial rewards.
        """
        # Check if the referrer exists and is a valid B2B user
        referrer = self.session.query(B2BUser).filter_by(id=referrer_id).first()
        if not referrer:
            raise ValueError("Referrer not found.")

        # Check if the referee has already been referred
        existing_referral = self.session.query(Referral).filter_by(referee_id=referee_id).first()
        if existing_referral:
            raise ValueError("This user has already been referred.")

        referral = Referral(
            referrer_id=referrer_id,
            referee_id=referee_id,
            status='active'  # The link is now immediately active
        )
        self.session.add(referral)
        self.session.commit()
        return referral

    def reward_referrer_for_order(self, referee_id, order_total_euros):
        """
        Awards loyalty points to a referrer based on their referee's order.
        This is called by the OrderService upon successful order completion.
        """
        referral = self.session.query(Referral).filter_by(referee_id=referee_id, status='active').first()
        
        # If the user was referred, calculate and award points to the referrer
        if referral:
            # Calculate points: 0.1 point per 1€ spent
            points_to_award = round(order_total_euros * 0.1, 2)
            
            if points_to_award > 0:
                self.loyalty_service.add_points(
                    user_id=referral.referrer_id,
                    user_type='b2b',
                    points=points_to_award,
                    reason=f"Referral bonus from order by user {referee_id}",
                    # Points expire one year from the date they are awarded
                    expires_at=datetime.utcnow() + timedelta(days=365)
                )
                
                # Optionally, create a reward record for tracking
                reward_record = ReferralReward(
                    referral_id=referral.id,
                    rewarded_user_id=referral.referrer_id,
                    points_awarded=points_to_award,
                    triggering_order_id=None # You can add the order ID here if available
                )
                self.session.add(reward_record)
                self.session.commit()
                
                # TODO: Trigger an email notification to the referrer
                # email_service.send_referral_reward_notification(referral.referrer_id, points_to_award)

                return points_to_award
        
        return 0
