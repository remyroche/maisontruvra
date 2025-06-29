from backend.database import db
from .base import BaseModel, SoftDeleteMixin
from .enums import OrderStatus

class Order(BaseModel, SoftDeleteMixin):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) 
    guest_email = db.Column(db.String(120), nullable=True)
    guest_phone = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(50), nullable=False, default='pending')

    b2b_account_id = db.Column(db.Integer, db.ForeignKey('b2b_accounts.id'), nullable=True)
    b2b_account = db.relationship('B2BAccount', backref='orders')

    total_cost = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    shipping_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable=True)
    
    # Link to the B2B Account instead of the individual user
    b2b_account_id = db.Column(db.Integer, db.ForeignKey('b2b_account.id'), nullable=True)
    
    # Store the specific user who created the order
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('b2b_user.id'), nullable=True)
    creator_ip_address = db.Column(db.String(45), nullable=True)
    b2b_account = db.relationship('B2BAccount', backref=db.backref('orders', lazy=True))
    created_by = db.relationship('B2BUser', backref=db.backref('orders_created', lazy=True))

    items = db.relationship('OrderItem', back_populates='order', cascade="all, delete-orphan")
    shipping_address = db.relationship('Address')
    invoice = db.relationship('Invoice', back_populates='order', uselist=False)

    def to_user_dict(self):
        """Serialization for the user viewing their own order."""
        return {
            'id': self.id,
            'order_number': self.order_number,
            'status': self.status.value,
            'total_amount': str(self.total_amount),
            'created_at': self.created_at.isoformat(),
            'items': [item.to_dict() for item in self.items],
            'shipping_address': self.shipping_address.to_dict() if self.shipping_address else None,
            'is_deleted': self.is_deleted
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
    price = db.Column(db.Numeric(10, 2), nullable=False) # Price at the time of purchase

    order = db.relationship('Order', back_populates='items')
    product = db.relationship('Product')

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'product_name': self.product.name,
            'quantity': self.quantity,
            'price': str(self.price),
            'is_deleted': self.is_deleted
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
