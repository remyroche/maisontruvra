from backend.models.base import Base
from backend.extensions import db
from decimal import Decimal


class Tier(Base):
    __tablename__ = 'tiers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    discount_percentage = db.Column(db.Numeric(5, 2), nullable=False, default=0.0)
    minimum_spend = db.Column(db.Numeric(10, 2), nullable=True)
    
    # A tier can have many B2B users
    users = db.relationship('User', back_populates='tier')

