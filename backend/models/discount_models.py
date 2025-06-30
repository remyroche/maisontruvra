# backend/models/discount_models.py

from .base import BaseModel
from . import db
from .enums import DiscountType, UserType

# Association table for discount-to-tier targeting
discount_loyalty_tiers = db.Table('discount_loyalty_tiers',
    db.Column('discount_id', db.Integer, db.ForeignKey('discount.id'), primary_key=True),
    db.Column('loyalty_tier_id', db.Integer, db.ForeignKey('loyalty_tier.id'), primary_key=True)
)

class Discount(BaseModel):
    __tablename__ = 'discount'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(80), unique=True, nullable=False)
    note = db.Column(db.String(255), nullable=True) # Note for the user
    
    discount_type = db.Column(db.Enum(DiscountType), nullable=False, default=DiscountType.PERCENTAGE)
    value = db.Column(db.Float, nullable=False)
    
    expiry_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Targeting Rules
    user_specific_type = db.Column(db.Enum(UserType), default=UserType.ALL, nullable=False) # b2c, b2b, or all
    
    # For discounts targeted at one specific user
    target_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    target_user = db.relationship('User', backref='specific_discounts')

    # For discounts targeted at specific loyalty tiers (many-to-many)
    restricted_to_tiers = db.relationship(
        'LoyaltyTier', 
        secondary=discount_loyalty_tiers,
        backref=db.backref('discounts', lazy='dynamic'),
        lazy='subquery'
    )
    
    # Track usage
    usages = db.relationship('DiscountUsage', back_populates='discount', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Discount {self.code}>'

class DiscountUsage(BaseModel):
    """Tracks which user has used a specific discount to enforce one-time use."""
    __tablename__ = 'discount_usage'

    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('discount_usages', lazy=True))
    
    discount_id = db.Column(db.Integer, db.ForeignKey('discount.id'), nullable=False)
    discount = db.relationship('Discount', back_populates='usages')

    # Ensure a user can only use a specific discount once
    __table_args__ = (db.UniqueConstraint('user_id', 'discount_id', name='_user_discount_uc'),)

    def __repr__(self):
        return f'<DiscountUsage user_id={self.user_id} discount_id={self.discount_id}>'
