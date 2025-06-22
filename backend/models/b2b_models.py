from backend.database import db
from .base import BaseModel
from .enums import B2BRequestStatus

class B2BUser(BaseModel):
    """
    Represents a B2B partner account, linked to a regular User.
    """
    __tablename__ = 'b2b_users'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(120), nullable=False)
    vat_number = db.Column(db.String(50), nullable=True, unique=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    tier_id = db.Column(db.Integer, db.ForeignKey('b2b_loyalty_tiers.id'), nullable=True)

    user = db.relationship('User', back_populates='b2b_account')
    tier = db.relationship('B2BLoyaltyTier', back_populates='b2b_users')

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'vat_number': self.vat_number,
            'user_id': self.user_id,
            'email': self.user.email,
            'tier': self.tier.name if self.tier else 'No Tier'
        }

class B2BPartnershipRequest(BaseModel):
    """
    Stores requests from users wanting to become B2B partners.
    """
    __tablename__ = 'b2b_partnership_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(120), nullable=False)
    vat_number = db.Column(db.String(50), nullable=True)
    contact_name = db.Column(db.String(120), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum(B2BRequestStatus), nullable=False, default=B2BRequestStatus.PENDING)

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'vat_number': self.vat_number,
            'contact_name': self.contact_name,
            'contact_email': self.contact_email,
            'message': self.message,
            'status': self.status.value,
            'created_at': self.created_at.isoformat()
        }