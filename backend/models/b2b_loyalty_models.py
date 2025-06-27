from backend.database import db
from backend.models.base import BaseModel
from datetime import datetime, timedelta
from sqlalchemy.dialects.postgresql import UUID
import uuid


class LoyaltyTier(BaseModel):
    """
    Represents a loyalty tier that can be configured by an administrator.
    e.g., Tier 1, Tier 2, etc.
    """
    __tablename__ = 'loyalty_tiers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    discount_percentage = db.Column(db.Float, nullable=False, default=0.0)
    min_spend = db.Column(db.Float, nullable=False, default=0.0)
    points_per_euro = db.Column(db.Float, nullable=False, default=1.0)
    benefits = db.Column(db.Text, nullable=True)

    # Relationship to users
    users = db.relationship('User', back_populates='loyalty_tier')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'discount_percentage': self.discount_percentage
        }

class UserLoyalty(db.Model):
    __tablename__ = 'user_loyalty'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    tier_id = db.Column(UUID(as_uuid=True), db.ForeignKey('loyalty_tiers.id'), nullable=False)
    points = db.Column(db.Integer, default=0)
    user = db.relationship('User', back_populates='loyalty')
    tier = db.relationship('LoyaltyTier')

class Referral(db.Model):
    __tablename__ = 'referrals'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referrer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    referred_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    referral_code = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(50), default='pending') # pending, completed
    reward_tier_id = db.Column(UUID(as_uuid=True), db.ForeignKey('referral_rewards.id'), nullable=True)
    referrer = db.relationship('User', foreign_keys=[referrer_id])
    referred = db.relationship('User', foreign_keys=[referred_id])
    reward_tier = db.relationship('ReferralRewardTier')

class ReferralRewardTier(db.Model):
    __tablename__ = 'referral_rewards'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referral_count = db.Column(db.Integer, unique=True, nullable=False)
    reward_description = db.Column(db.String(255), nullable=False)

class PointVoucher(db.Model):
    __tablename__ = 'point_vouchers'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    voucher_code = db.Column(db.String(50), unique=True, nullable=False)
    points_cost = db.Column(db.Integer, nullable=False)
    discount_amount = db.Column(db.Float, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    user = db.relationship('User')

class ExclusiveReward(db.Model):
    __tablename__ = 'exclusive_rewards'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    points_cost = db.Column(db.Integer, nullable=False)
    reward_type = db.Column(db.String(50), nullable=False) # e.g., 'product', 'experience', 'content'
    tier_id = db.Column(UUID(as_uuid=True), db.ForeignKey('loyalty_tiers.id'), nullable=True)
    tier = db.relationship('LoyaltyTier')



class LoyaltyPointTransaction(BaseModel):
    """
    A log of every loyalty point transaction.
    A user's balance is the sum of all their non-expired points.
    """
    __tablename__ = 'loyalty_point_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    points = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(255), nullable=False) # e.g., "Order #1234", "Referral Bonus"
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(days=365))
    is_expired = db.Column(db.Boolean, default=False, index=True)
    
    user = db.relationship('User', backref=db.backref('point_transactions', lazy=True))
