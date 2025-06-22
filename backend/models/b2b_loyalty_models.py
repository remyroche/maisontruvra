from backend.database import db
from .base import BaseModel

class B2BLoyaltyTier(BaseModel):
    """
    Represents different tiers in the B2B loyalty program.
    A tier can be defined by an absolute minimum spend or a percentage of top spenders.
    """
    __tablename__ = 'b2b_loyalty_tiers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    min_spend = db.Column(db.Numeric(10, 2), nullable=True)  # Absolute spend to qualify
    percentage = db.Column(db.Integer, nullable=True)  # Top X% of spenders
    benefits = db.Column(db.Text, nullable=True) # Description of benefits
    
    b2b_users = db.relationship('B2BUser', back_populates='tier')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'min_spend': str(self.min_spend) if self.min_spend else None,
            'percentage': self.percentage,
            'benefits': self.benefits
        }
