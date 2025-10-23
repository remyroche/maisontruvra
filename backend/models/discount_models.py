# backend/models/discount_models.py

import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID

from .. import db
from .enums import DiscountType  # <-- Correctly import the Enum


class Discount(db.Model):
    __tablename__ = "discounts"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = db.Column(db.String(100), unique=True, nullable=False)

    # Use the Enum for the discount_type column
    discount_type = db.Column(db.Enum(DiscountType), nullable=False)

    value = db.Column(db.Float, nullable=False)
    
    # Enhanced fields for specific targeting
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    max_uses = db.Column(db.Integer, nullable=True)
    times_used = db.Column(db.Integer, default=0)
    
    # Targeting fields
    target_type = db.Column(db.String(20), default="general")  # general, user, product, tier
    target_user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=True)
    target_product_id = db.Column(UUID(as_uuid=True), db.ForeignKey("products.id"), nullable=True)
    target_tier_id = db.Column(db.Integer, db.ForeignKey("tiers.id"), nullable=True)
    
    # Minimum requirements
    minimum_spend = db.Column(db.Numeric(10, 2), nullable=True)
    minimum_quantity = db.Column(db.Integer, nullable=True)

    # Relationships
    usage = db.relationship("DiscountUsage", back_populates="discount")
    target_user = db.relationship("User", foreign_keys=[target_user_id])
    target_product = db.relationship("Product", foreign_keys=[target_product_id])
    target_tier = db.relationship("Tier", foreign_keys=[target_tier_id])

    def __repr__(self):
        return f"<Discount {self.code}>"


class DiscountUsage(db.Model):
    __tablename__ = "discount_usage"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    discount_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("discounts.id"), nullable=False
    )
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)

    # Relationships
    discount = db.relationship("Discount", back_populates="usage")
    user = db.relationship("User")

    def __repr__(self):
        return f"<DiscountUsage for {self.discount.code} by {self.user.username}>"
