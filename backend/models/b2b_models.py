from backend.database import db
from .base import BaseModel
from .enums import B2BRequestStatus


# Represents the parent company account
class B2BAccount(db.Model):
    __tablename__ = 'b2b_account'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(120), nullable=False)
    siret = db.Column(db.String(14), unique=True, nullable=False)
    status = db.Column(db.String(50), default='pending', nullable=False) # pending, approved, rejected
    
    # Relationship to all users under this company
    users = db.relationship('B2BUser', back_populates='account')
    
    def __repr__(self):
        return f'<B2BAccount {self.company_name}>'

# Represents an individual user belonging to a company
class B2BUser(db.Model):
    __tablename__ = 'b2b_user'
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Key to the parent B2BAccount
    account_id = db.Column(db.Integer, db.ForeignKey('b2b_account.id'), nullable=False)
    
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Role to distinguish permissions within the account
    role = db.Column(db.String(50), default='member', nullable=False) # 'admin' or 'member'

    mfa_secret = db.Column(EncryptedType(db.String, Config.SECRET_KEY), nullable=True)
    mfa_enabled = db.Column(db.Boolean, default=False)

    # Relationship back to the parent account
    account = db.relationship('B2BAccount', back_populates='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<B2BUser {self.email}>'


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
