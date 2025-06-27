import secrets
from sqlalchemy.orm import joinedload
from .. import db
from ..models import User, LoyaltyTier, UserLoyalty, Referral, ReferralRewardTier, PointVoucher, ExclusiveReward, LoyaltyPointLog
from ..services.notification_service import NotificationService

class LoyaltyService:

    @staticmethod
    def get_all_tiers():
        return LoyaltyTier.query.order_by(LoyaltyTier.min_spend).all()

    @staticmethod
    def create_tier(name, min_spend, points_per_euro, benefits):
        tier = LoyaltyTier(name=name, min_spend=float(min_spend), points_per_euro=float(points_per_euro), benefits=benefits)
        db.session.add(tier)
        db.session.commit()
        return tier

    @staticmethod
    def update_loyalty_tier(tier_id, data):
        tier = LoyaltyTier.query.get(tier_id)
        if tier:
            tier.name = data.get('name', tier.name)
            tier.min_spend = float(data.get('min_spend', tier.min_spend))
            tier.points_per_euro = float(data.get('points_per_euro', tier.points_per_euro))
            tier.benefits = data.get('benefits', tier.benefits)
            db.session.commit()
        return tier

    @staticmethod
    def delete_tier(tier_id):
        tier = LoyaltyTier.query.get(tier_id)
        if tier:
            # Check if any users are in this tier before deleting
            if UserLoyalty.query.filter_by(tier_id=tier_id).first():
                raise ValueError("Cannot delete tier with assigned users.")
            db.session.delete(tier)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_user_loyalty_status(user_id):
        user_loyalty = UserLoyalty.query.options(joinedload(UserLoyalty.tier)).filter_by(user_id=user_id).first()
        if not user_loyalty:
            return LoyaltyService.create_initial_loyalty_status(user_id)
        return user_loyalty
        
    @staticmethod
    def create_initial_loyalty_status(user_id):
        # Find the base tier (usually the one with 0 min_spend)
        base_tier = LoyaltyTier.query.order_by(LoyaltyTier.min_spend).first()
        if not base_tier:
             raise Exception("No base loyalty tier found in the system.")
             
        user_loyalty = UserLoyalty(user_id=user_id, tier_id=base_tier.id, points=0)
        db.session.add(user_loyalty)
        db.session.commit()
        return user_loyalty

    @staticmethod
    def adjust_points(user_id, points_change, reason, admin_user_id=None):
        user_loyalty = LoyaltyService.get_user_loyalty_status(user_id)
        user_loyalty.points += points_change
        
        log_entry = LoyaltyPointLog(
            user_id=user_id,
            points_change=points_change,
            reason=reason,
            changed_by_admin_id=admin_user_id
        )
        db.session.add(log_entry)
        db.session.commit()
        
        # Check if user qualifies for a tier upgrade
        LoyaltyService.update_user_tier(user_id)
        
        return user_loyalty.points

    @staticmethod
    def update_user_tier(user_id):
        # Logic to check user's total spending and update their tier
        pass # To be implemented based on spending calculation

    @staticmethod
    def get_points_breakdown(user_id):
        return LoyaltyPointLog.query.filter_by(user_id=user_id).order_by(LoyaltyPointLog.created_at.desc()).all()

    @staticmethod
    def get_referral_data(user_id):
        return Referral.query.filter_by(referrer_id=user_id).first()
        
    @staticmethod
    def create_referral_code(user_id):
        user = User.query.get(user_id)
        if not user:
            return None
            
        existing_referral = Referral.query.filter_by(referrer_id=user_id).first()
        if existing_referral:
            return existing_referral

        code = f"{user.first_name.upper()}-{secrets.token_hex(3)}".upper()
        while Referral.query.filter_by(referral_code=code).first():
             code = f"{user.first_name.upper()}-{secrets.token_hex(3)}".upper()

        referral = Referral(referrer_id=user_id, referral_code=code)
        db.session.add(referral)
        db.session.commit()
        return referral

    @staticmethod
    def get_referrals_for_user(user_id):
        return Referral.query.filter_by(referrer_id=user_id).all()

    @staticmethod
    def get_referral_reward_tiers():
        return ReferralRewardTier.query.order_by(ReferralRewardTier.referral_count).all()

    @staticmethod
    def create_referral_reward_tier(data):
        reward_tier = ReferralRewardTier(**data)
        db.session.add(reward_tier)
        db.session.commit()
        return reward_tier

    @staticmethod
    def convert_points_to_voucher(user_id, points_to_convert, discount_amount):
        user_loyalty = LoyaltyService.get_user_loyalty_status(user_id)
        if user_loyalty and user_loyalty.points >= points_to_convert:
            user_loyalty.points -= points_to_convert
            voucher_code = f"VOUCHER-{secrets.token_hex(4)}".upper()
            voucher = PointVoucher(
                user_id=user_id,
                voucher_code=voucher_code,
                points_cost=points_to_convert,
                discount_amount=discount_amount
            )
            LoyaltyService.adjust_points(user_id, -points_to_convert, f"Converted to voucher {voucher_code}")
            db.session.add(voucher)
            db.session.commit()
            return voucher
        return None

    @staticmethod
    def get_exclusive_rewards(user_id):
        user_loyalty = LoyaltyService.get_user_loyalty_status(user_id)
        return ExclusiveReward.query.filter(ExclusiveReward.tier_id <= user_loyalty.tier_id).all()

    @staticmethod
    def redeem_exclusive_reward(user_id, reward_id):
        user_loyalty = LoyaltyService.get_user_loyalty_status(user_id)
        reward = ExclusiveReward.query.get(reward_id)
        
        if user_loyalty and reward and user_loyalty.points >= reward.points_cost:
            reason = f"Redeemed exclusive reward: {reward.name}"
            LoyaltyService.adjust_points(user_id, -reward.points_cost, reason)
            
            # Here you would add logic based on reward type
            # For example, send an email or add a product to the next order
            NotificationService.send_reward_redemption_email(user_id, reward)

            db.session.commit()
            return True
        return False
