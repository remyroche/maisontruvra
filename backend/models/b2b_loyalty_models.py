from sqlalchemy.dialects.postgresql import UUID
import uuid
from .. import db
from .base import Base

class LoyaltyTier(Base):
    __tablename__ = 'loyalty_tiers'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False, unique=True)
    min_spend = db.Column(db.Float, nullable=False, default=0.0)
    points_per_euro = db.Column(db.Float, nullable=False, default=1.0)
    benefits = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'min_spend': self.min_spend,
            'points_per_euro': self.points_per_euro,
            'benefits': self.benefits
        }

class UserLoyalty(Base):
    __tablename__ = 'user_loyalty'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False, unique=True)
    tier_id = db.Column(UUID(as_uuid=True), db.ForeignKey('loyalty_tiers.id'), nullable=False)
    points = db.Column(db.Integer, default=0)
    
    user = db.relationship('User', back_populates='loyalty')
    tier = db.relationship('LoyaltyTier')

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'points': self.points,
            'tier': self.tier.to_dict() if self.tier else None,
        }

class LoyaltyPointLog(Base):
    __tablename__ = 'loyalty_point_logs'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    points_change = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    order_id = db.Column(UUID(as_uuid=True), db.ForeignKey('orders.id'), nullable=True)
    changed_by_admin_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)

    def to_dict(self):
        return {
            'id': str(self.id),
            'points_change': self.points_change,
            'reason': self.reason,
            'created_at': self.created_at.isoformat()
        }

class Referral(Base):
    __tablename__ = 'referrals'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referrer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    referred_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    referral_code = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, completed
    
    referrer = db.relationship('User', foreign_keys=[referrer_id])
    referred = db.relationship('User', foreign_keys=[referred_id])

    def to_dict(self):
        return {
            'id': str(self.id),
            'referral_code': self.referral_code,
            'status': self.status,
            'referred_user_email': self.referred.email if self.referred else None,
            'created_at': self.created_at.isoformat()
        }

class ReferralRewardTier(Base):
    __tablename__ = 'referral_rewards'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referral_count = db.Column(db.Integer, unique=True, nullable=False)
    reward_description = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            'id': str(self.id),
            'referral_count': self.referral_count,
            'reward_description': self.reward_description
        }

class PointVoucher(Base):
    __tablename__ = 'point_vouchers'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    voucher_code = db.Column(db.String(50), unique=True, nullable=False)
    points_cost = db.Column(db.Integer, nullable=False)
    discount_amount = db.Column(db.Float, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    user = db.relationship('User')

    def to_dict(self):
        return {
            'id': str(self.id),
            'voucher_code': self.voucher_code,
            'points_cost': self.points_cost,
            'discount_amount': self.discount_amount,
            'is_used': self.is_used
        }

class ExclusiveReward(Base):
    __tablename__ = 'exclusive_rewards'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    points_cost = db.Column(db.Integer, nullable=False)
    reward_type = db.Column(db.String(50), nullable=False)
    tier_id = db.Column(UUID(as_uuid=True), db.ForeignKey('loyalty_tiers.id'), nullable=False)
    tier = db.relationship('LoyaltyTier')
    linked_product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('products.id'), nullable=True)
    linked_product = db.relationship('Product')

    def to_dict(self):
        # ... existing to_dict ...
        data = {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'points_cost': self.points_cost,
            'reward_type': self.reward_type,
            'required_tier': self.tier.name if self.tier else None,
            'linked_product_id': str(self.linked_product_id) if self.linked_product_id else None
        }
        return data

