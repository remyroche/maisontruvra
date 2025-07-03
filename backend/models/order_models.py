from backend.database import db
from .base import BaseModel, SoftDeleteMixin
from .enums import OrderStatus
import enum

class OrderStatusEnum(enum.Enum):
    CONFIRMED = 'Confirmed'
    PACKING = 'Packing'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'
    CANCELLED = 'Cancelled'
    
class Order(BaseModel, SoftDeleteMixin):
    __tablename__ = 'orders'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) 
    guest_email = db.Column(db.String(120), nullable=True)
    guest_phone = db.Column(db.String(20), nullable=True)
    
    # B2B functionality
    b2b_account_id = db.Column(db.Integer, db.ForeignKey('b2b_accounts.id'), nullable=True)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    creator_ip_address = db.Column(db.String(45), nullable=True)
    
    total_cost = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    shipping_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable=True)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    b2b_account = db.relationship('B2BAccount', backref='orders')
    created_by = db.relationship('User', foreign_keys=[created_by_user_id])

    items = db.relationship('OrderItem', back_populates='order', cascade="all, delete-orphan")
    shipping_address = db.relationship('Address')
    invoice = db.relationship('Invoice', back_populates='order', uselist=False)

    items = db.relationship('OrderItem', backref='order', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_price': self.total_price,
            'created_at': self.created_at.isoformat(),
            'order_status': self.order_status.value,
            'tracking_number': self.tracking_number,
            'tracking_url': self.tracking_url,
            'items': [item.to_dict() for item in self.items]
        }


    def to_admin_dict(self):
        """Serialization for an admin viewing an order."""
        data = self.to_user_dict()
        data['user'] = self.user.to_public_dict()
        return data

    def to_dict(self, view='user'):
        if view == 'admin':
            return self.to_admin_dict()
        return self.to_user_dict()

class OrderItem(BaseModel, SoftDeleteMixin):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)

    order = db.relationship('Order', back_populates='items')
    product = db.relationship('Product')


    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name,
            'quantity': self.quantity,
            'price_at_purchase': self.price_at_purchase
        }


class Invoice(BaseModel, SoftDeleteMixin):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, unique=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    pdf_path = db.Column(db.String(255))
    
    order = db.relationship('Order', back_populates='invoice')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'invoice_number': self.invoice_number,
            'created_at': self.created_at.isoformat(),
            'is_deleted': self.is_deleted
        }
