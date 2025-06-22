from backend.database import db
from .base import BaseModel

class B2BReferral(BaseModel):
    __tablename__ = 'b2b_referrals'
    id = db.Column(db.Integer, primary_key=True)
    
    # The B2B user who made the referral
    referrer_id = db.Column(db.Integer, db.ForeignKey('b2b_users.id'), nullable=False)
    
    # Information about the referred company
    referred_company_name = db.Column(db.String(120), nullable=False)
    referred_contact_email = db.Column(db.String(120), nullable=False)
    
    status = db.Column(db.String(50), default='pending') # pending, contacted, converted
    
    referrer = db.relationship('B2BUser', backref='referrals')

    def to_dict(self):
        return {
            'id': self.id,
            'referrer_company': self.referrer.company_name,
            'referred_company_name': self.referred_company_name,
            'referred_contact_email': self.referred_contact_email,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
