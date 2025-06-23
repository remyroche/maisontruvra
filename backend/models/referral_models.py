from backend.database import db
from .base import BaseModel

class Referral(BaseModel):
    """
    Tracks the relationship between a referrer and a referred user.
    """
    __tablename__ = 'referrals'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # The user who was referred
    referred_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # The user who did the referring
    referrer_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # The user who was referred
    referred = db.relationship('User', foreign_keys=[referred_user_id], backref=db.backref('referral_entry', uselist=False))
    
    # The user who did the referring
    referrer = db.relationship('User', foreign_keys=[referrer_user_id], backref='referrals_made')

