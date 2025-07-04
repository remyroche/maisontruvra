import uuid
from sqlalchemy.dialects.postgresql import (
    UUID as pgUUID,
)  # Use a distinct alias for PostgreSQL UUID
from .. import db
from .base import BaseModel, SoftDeleteMixin  # Assuming you have these base models

# ==============================================================================
# Serialized Item Model
# ==============================================================================


class SerializedItem(BaseModel, SoftDeleteMixin):
    """
    Represents a single, unique, physical instance of a product,
    each with its own unique identifier (UID).
    """

    __tablename__ = "serialized_items"

    id = db.Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = db.Column(
        pgUUID(as_uuid=True), db.ForeignKey("products.id"), nullable=False
    )

    # The human-readable Unique Identifier for this specific item.
    uid = db.Column(db.String(255), unique=True, nullable=False, index=True)

    status = db.Column(
        db.String(50), nullable=False, default="created", index=True
    )  # E.g., 'created', 'in_stock', 'sold'
    order_item_id = db.Column(
        pgUUID(as_uuid=True), db.ForeignKey("order_items.id"), nullable=True
    )  # Link when sold

    # --- Relationships ---
    product = db.relationship("Product", back_populates="serialized_items")
    passport = db.relationship(
        "ProductPassport",
        back_populates="serialized_item",
        uselist=False,
        cascade="all, delete-orphan",
    )
    order_item = db.relationship("OrderItem")

    def __repr__(self):
        return f"<SerializedItem UID: {self.uid} for Product ID: {self.product_id}>"


# ==============================================================================
# Product Passport Models
# ==============================================================================


class ProductPassport(BaseModel, SoftDeleteMixin):
    """
    The digital passport, which is uniquely linked to a single SerializedItem.
    It contains a chronological log of events related to that specific item.
    """

    __tablename__ = "product_passports"

    id = db.Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # This is the key change: The passport is now linked to a unique item, not a product.
    serialized_item_id = db.Column(
        pgUUID(as_uuid=True),
        db.ForeignKey("serialized_items.id"),
        nullable=False,
        unique=True,
    )

    # --- Relationships ---
    serialized_item = db.relationship("SerializedItem", back_populates="passport")
    entries = db.relationship(
        "PassportEntry",
        back_populates="passport",
        cascade="all, delete-orphan",
        order_by="PassportEntry.timestamp.desc()",
    )

    def to_dict_detailed(self):
        """Serializes the passport with its full history for detailed views."""
        return {
            "passport_id": str(self.id),
            "item_uid": self.serialized_item.uid,
            "product_name": self.serialized_item.product.name,
            "created_at": self.created_at.isoformat(),
            "entries": [entry.to_dict() for entry in self.entries],
        }


class PassportEntry(BaseModel, SoftDeleteMixin):
    """
    A single event or entry in the lifecycle of a ProductPassport.
    """

    __tablename__ = "passport_entries"

    id = db.Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    passport_id = db.Column(
        pgUUID(as_uuid=True), db.ForeignKey("product_passports.id"), nullable=False
    )

    # --- Entry Details ---
    event_type = db.Column(
        db.String(100), nullable=False
    )  # E.g., 'MANUFACTURED', 'SHIPPED', 'DELIVERED'
    details = db.Column(db.Text)
    timestamp = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )

    # --- Relationship ---
    passport = db.relationship("ProductPassport", back_populates="entries")

    def to_dict(self):
        """Serializes a single passport entry."""
        return {
            "event_type": self.event_type,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }
