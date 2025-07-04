from backend.extensions import db
from backend.models.base import BaseModel

from .enums import B2BRequestStatus, B2BStatus


class Tier(BaseModel):
    __tablename__ = "tiers"
    name = db.Column(db.String(50), unique=True, nullable=False)
    discount_percentage = db.Column(db.Numeric(5, 2), nullable=False, default=0.0)
    minimum_spend = db.Column(db.Numeric(10, 2), nullable=True)

    # A tier can have many B2B users
    users = db.relationship("User", back_populates="tier")


class B2BTier(BaseModel):
    """B2B Tier model for managing different B2B partnership levels"""

    __tablename__ = "b2b_tiers"

    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    discount_percentage = db.Column(db.Numeric(5, 2), nullable=False, default=0.0)
    minimum_order_value = db.Column(db.Numeric(10, 2), nullable=True)
    credit_limit = db.Column(db.Numeric(12, 2), nullable=True)
    payment_terms_days = db.Column(db.Integer, default=30)

    # Relationships
    accounts = db.relationship("B2BAccount", back_populates="tier")


class Company(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    vat_number = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(
        db.String(50), default="pending"
    )  # ex: pending, approved, rejected

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    # La relation est définie avec back_populates pour correspondre au modèle User
    users = db.relationship("User", back_populates="company")

    def __repr__(self):
        return f"<Company {self.name}>"


class B2BAccount(BaseModel):
    """B2B Account model for managing business customer accounts"""

    __tablename__ = "b2b_accounts"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    company_registration_number = db.Column(db.String(100), nullable=True)
    tax_id = db.Column(db.String(50), nullable=True)
    tier_id = db.Column(db.Integer, db.ForeignKey("b2b_tiers.id"), nullable=True)
    status = db.Column(db.Enum(B2BStatus), default=B2BStatus.PENDING, nullable=False)
    credit_limit = db.Column(db.Numeric(12, 2), nullable=True)
    current_balance = db.Column(db.Numeric(12, 2), default=0.0, nullable=False)
    payment_terms_days = db.Column(db.Integer, default=30)
    approved_at = db.Column(db.DateTime, nullable=True)
    approved_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Relationships
    user = db.relationship("User", foreign_keys=[user_id], back_populates="b2b_account")
    tier = db.relationship("B2BTier", back_populates="accounts")
    approved_by = db.relationship("User", foreign_keys=[approved_by_id])


class B2BPartnershipRequest(BaseModel):
    """B2B Partnership Request model for managing partnership applications"""

    __tablename__ = "b2b_partnership_requests"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    company_registration_number = db.Column(db.String(100), nullable=True)
    tax_id = db.Column(db.String(50), nullable=True)
    business_type = db.Column(db.String(100), nullable=True)
    annual_revenue = db.Column(db.Numeric(15, 2), nullable=True)
    number_of_employees = db.Column(db.Integer, nullable=True)
    website = db.Column(db.String(255), nullable=True)
    business_description = db.Column(db.Text, nullable=True)
    requested_tier_id = db.Column(
        db.Integer, db.ForeignKey("b2b_tiers.id"), nullable=True
    )
    status = db.Column(
        db.Enum(B2BRequestStatus), default=B2BRequestStatus.PENDING, nullable=False
    )
    notes = db.Column(db.Text, nullable=True)  # Admin notes
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Relationships
    user = db.relationship("User", foreign_keys=[user_id])
    requested_tier = db.relationship("B2BTier")
    reviewed_by = db.relationship("User", foreign_keys=[reviewed_by_id])
