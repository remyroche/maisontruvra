from backend.database import db
from .base import BaseModel
from datetime import datetime

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
