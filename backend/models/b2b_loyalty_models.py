from backend.database import db
from backend.models.base import BaseModel
from datetime import datetime, timedelta

class LoyaltyTier(BaseModel):
    """
    Represents a loyalty tier that can be configured by an administrator.
    e.g., Tier 1, Tier 2, etc.
    """
    __tablename__ = 'loyalty_tiers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    discount_percentage = db.Column(db.Float, nullable=False, default=0.0)
    
    # Relationship to users
    users = db.relationship('User', back_populates='loyalty_tier')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'discount_percentage': self.discount_percentage
        }


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
