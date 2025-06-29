from backend.database import db
from .base import BaseModel
from datetime import datetime


class Referral(db.Model):
    __tablename__ = 'referral'
    id = db.Column(db.Integer, primary_key=True)
    
    # The B2B user who made the referral
    referrer_id = db.Column(db.Integer, db.ForeignKey('b2b_user.id'), nullable=False)
    
    # The new B2B user who was referred
    referee_id = db.Column(db.Integer, db.ForeignKey('b2b_user.id'), nullable=False, unique=True)
    
    # Simplified status: 'active' once the link is made. No more 'pending' or 'completed'.
    status = db.Column(db.String(50), default='active', nullable=False) 
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    referrer = db.relationship('B2BUser', foreign_keys=[referrer_id])
    referee = db.relationship('B2BUser', foreign_keys=[referee_id])


class ReferralReward(db.Model):
    """
    A log to track each time a referrer is rewarded.
    """
    __tablename__ = 'referral_reward'
    id = db.Column(db.Integer, primary_key=True)
    referral_id = db.Column(db.Integer, db.ForeignKey('referral.id'), nullable=False)
    
    # The user who received the reward (the referrer)
    rewarded_user_id = db.Column(db.Integer, db.ForeignKey('b2b_user.id'), nullable=False)
    
    points_awarded = db.Column(db.Float, nullable=False)
    
    # Optional: Link to the specific order that triggered the reward
    triggering_order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime)

    referral = db.relationship('Referral', backref=db.backref('rewards', lazy=True))
