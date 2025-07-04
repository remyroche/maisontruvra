# backend/models/discount_models.py

from .. import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .enums import DiscountType  # <-- Correctly import the Enum


class Discount(db.Model):
    __tablename__ = "discounts"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = db.Column(db.String(100), unique=True, nullable=False)

    # Use the Enum for the discount_type column
    discount_type = db.Column(db.Enum(DiscountType), nullable=False)

    value = db.Column(db.Float, nullable=False)

    # Relationship to track usage
    usage = db.relationship("DiscountUsage", back_populates="discount")

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
