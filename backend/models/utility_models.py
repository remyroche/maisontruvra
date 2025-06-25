from backend.database import db
from .base import BaseModel
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

class StockNotification(db.Model):
    """
    Stores user requests to be notified when a product is back in stock.
    """
    __tablename__ = 'stock_notifications'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    guest_email = db.Column(db.String(120), nullable=True, index=True)
    
    # To prevent sending multiple emails for the same restock event.
    notified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product')
    user = db.relationship('User')

    # Add unique constraints to prevent a user/guest from signing up multiple times for the same product.
    __table_args__ = (
        db.UniqueConstraint('product_id', 'user_id', name='_product_user_uc'),
        db.UniqueConstraint('product_id', 'guest_email', name='_product_guest_email_uc')
    )

    def __repr__(self):
        return f'<StockNotification for Product {self.product_id}>'



class Setting(BaseModel):
    """
    A simple key-value store for site-wide settings.
    """
    __tablename__ = 'settings'
    # Use key as primary key instead of auto-incrementing id
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(JSONB) # Use JSONB to store various types of values

    # Override the default id from BaseModel
    id = None 

    def to_dict(self):
        return {
            'key': self.key,
            'value': self.value
        }
