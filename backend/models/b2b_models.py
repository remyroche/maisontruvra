from backend.database import db
from .base import BaseModel, SoftDeleteMixin
from .enums import B2BRequestStatus
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from sqlalchemy_utils import EncryptedType
from flask import current_app
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Enum, Numeric
from sqlalchemy.orm import relationship
from .enums import B2BStatus


class Tier(Base):
    """
    Represents a B2B pricing tier.
    Each B2B user is assigned to a tier, which determines their discount percentage.
    """
    __tablename__ = 'b2b_tiers'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    discount_percentage = Column(Numeric(5, 2), nullable=False, default=0.00)
    minimum_spend = Column(Numeric(10, 2), nullable=True)  # Optional minimum annual spend to qualify

    # Relationship to B2BUser
    b2b_users = relationship("B2BUser", back_populates="tier")

    def __repr__(self):
        return f"<Tier {self.name} ({self.discount_percentage}%)>"


# Represents the parent company account
class B2BAccount(db.Model):
    __tablename__ = 'b2b_users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    company_name = Column(String(120), nullable=False)
    vat_number = Column(String(50), nullable=True, unique=True)
    status = Column(Enum(B2BStatus), default=B2BStatus.PENDING)

    # Foreign Key to Tier
    tier_id = Column(Integer, ForeignKey('b2b_tiers.id'), nullable=True)

    # Relationships
    user = relationship("User", back_populates="b2b_user")
    tier = relationship("Tier", back_populates="b2b_users")  # Link to the tier
    teams = relationship("Team", back_populates="b2b_user")
    invitations = relationship("B2BInvitation", back_populates="invited_by")

class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    b2b_user_id = Column(Integer, ForeignKey('b2b_users.id'))
    b2b_user = relationship("B2BUser", back_populates="teams")
    members = relationship("TeamMember", back_populates="team")


class TeamMember(Base):
    __tablename__ = 'team_members'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    # Define role, e.g., admin, member
    role = Column(String(50), default='member')
    
    user = relationship("User")
    team = relationship("Team", back_populates="members")


class B2BInvitation(Base):
    __tablename__ = 'b2b_invitations'
    id = Column(Integer, primary_key=True)
    email = Column(String(120), nullable=False)
    token = Column(String(100), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    invited_by_id = Column(Integer, ForeignKey('b2b_users.id'))
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=True)
    is_accepted = Column(Boolean, default=False)
    
    invited_by = relationship("B2BUser", back_populates="invitations")
    team = relationship("Team")


# Represents an individual user belonging to a company
class B2BUser(db.Model):
    __tablename__ = 'b2b_user'
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Key to the parent B2BAccount
    account_id = db.Column(db.Integer, db.ForeignKey('b2b_account.id'), nullable=False)
    language = db.Column(db.String(10), default='fr', nullable=False)

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Role to distinguish permissions within the account
    role = db.Column(db.String(50), default='member', nullable=False) # 'admin' or 'member'

    mfa_secret = db.Column(EncryptedType(db.String, lambda: current_app.config['SECRET_KEY']), nullable=True)
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
