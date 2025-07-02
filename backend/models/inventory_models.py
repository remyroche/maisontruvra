from backend.database import db
from .base import BaseModel
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Item(db.Model):
    """
    Represents a specific, sellable instance or batch of a Product.
    This is the core of our inventory.
    """
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    
    # A unique identifier for this specific item/batch (e.g., for passports)
    uid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to the parent Product template
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Optional foreign key to a Collection
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'), nullable=True)
    
    # --- Item-Specific, Potentially Overridden Fields ---
    
    # If null, the item uses the parent product's value. If set, it overrides it.
    price = db.Column(db.Float, nullable=True) 
    producer_notes = db.Column(db.Text, nullable=True)
    pairing_suggestions = db.Column(db.Text, nullable=True)
    
    # --- Item-Specific Fields ---
    
    stock_quantity = db.Column(db.Integer, nullable=False, default=1)
    creation_date = db.Column(db.Date, nullable=False, default=db.func.current_date())
    harvest_date = db.Column(db.Date, nullable=True) # <-- NEW FIELD
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    product = db.relationship('Product', backref='items')
    collection = db.relationship('Collection', backref='items')

    def to_dict(self):
        """Serializes the Item object to a dictionary."""
        # Use parent product's info as a fallback for overridable fields
        final_price = self.price if self.price is not None else self.product.price
        final_producer_notes = self.producer_notes if self.producer_notes is not None else self.product.producer_notes
        final_pairing_suggestions = self.pairing_suggestions if self.pairing_suggestions is not None else self.product.pairing_suggestions

        return {
            'id': self.id,
            'uid': str(self.uid),
            'product_id': self.product_id,
            'product_name': self.product.name,
            'product_sku': self.product.sku,
            'collection_id': self.collection_id,
            'collection_name': self.collection.name if self.collection else None,
            'price': final_price,
            'producer_notes': final_producer_notes,
            'pairing_suggestions': final_pairing_suggestions,
            'stock_quantity': self.stock_quantity,
            'creation_date': self.creation_date.isoformat(),
            'harvest_date': self.harvest_date.isoformat() if self.harvest_date else None, # <-- NEW FIELD
            'is_active': self.is_active
        }


class Inventory(BaseModel):
    __tablename__ = 'inventories'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, unique=True)
    quantity = db.Column(db.Integer, default=0)
    low_stock_threshold = db.Column(db.Integer, default=10)
    product = db.relationship('Product', back_populates='inventory')
    reservations = db.relationship('InventoryReservation', backref='inventory_item', lazy='dynamic', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'product_name': self.product.name,
            'sku': self.product.sku,
            'quantity': self.quantity
        }

    @property
    def available_quantity(self):
        """Calculates the quantity available for purchase (total - reserved)."""
        reserved = db.session.query(db.func.sum(InventoryReservation.quantity)).filter_by(inventory_id=self.id).scalar() or 0
        return self.quantity - reserved

    def __repr__(self):
        return f'<Inventory for Product {self.product_id}>'

class StockNotificationRequest(BaseModel):
    __tablename__ = 'stock_notification_requests'
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    notified_at = db.Column(db.DateTime, nullable=True)
    
    product = db.relationship('Product')

    __table_args__ = (db.UniqueConstraint('product_id', 'email', name='_product_email_uc'),)

class InventoryReservation(db.Model):
    __tablename__ = 'inventory_reservations'
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    # Use session_id for guests and user_id for logged-in users.
    session_id = db.Column(db.String(255), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Reservation {self.id} for Inventory {self.inventory_id}>'
