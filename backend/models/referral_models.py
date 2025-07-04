from datetime import datetime

from backend.extensions import db

from .base import BaseModel


class Referral(db.Model):
    __tablename__ = "referrals"
    id = db.Column(db.Integer, primary_key=True)
    # The user who made the referral
    referrer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    referred_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True
    )

    reward_points_awarded = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default="active", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    referrer = db.relationship(
        "User", foreign_keys=[referrer_id], back_populates="referrals_made"
    )
    referred = db.relationship("User", foreign_keys=[referred_id])


class ReferralTier(BaseModel):
    __tablename__ = "referral_tiers"
    name = db.Column(db.String(50), unique=True, nullable=False)
    min_referrals = db.Column(db.Integer, nullable=False)
    points_multiplier = db.Column(db.Float, default=1.0)
    description = db.Column(db.Text, nullable=True)

    users = db.relationship("User", back_populates="referral_tier")


class ReferralReward(db.Model):
    """
    A log to track each time a referrer is rewarded.
    """

    __tablename__ = "referral_reward"
    id = db.Column(db.Integer, primary_key=True)
    referral_id = db.Column(db.Integer, db.ForeignKey("referral.id"), nullable=False)

    # The user who received the reward (the referrer)
    rewarded_user_id = db.Column(
        db.Integer, db.ForeignKey("b2b_user.id"), nullable=False
    )

    points_awarded = db.Column(db.Float, nullable=False)

    # Optional: Link to the specific order that triggered the reward
    triggering_order_id = db.Column(
        db.Integer, db.ForeignKey("order.id"), nullable=True
    )

    created_at = db.Column(db.DateTime, default=datetime)

    referral = db.relationship("Referral", backref=db.backref("rewards", lazy=True))
