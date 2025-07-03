import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .. import db # Use relative import to avoid circular dependencies
from .base import BaseModel, SoftDeleteMixin # Assuming these are in a 'base.py' file

# --- Enum Definition ---
# This Enum now includes all necessary statuses and is defined *before* the model.
class OrderStatusEnum(enum.Enum):
    PENDING = 'Pending'
    CONFIRMED = 'Confirmed'
    PROCESSING = 'Processing' # Added PROCESSING for consistency
    PACKING = 'Packing'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'
    CANCELLED = 'Cancelled'

# --- Model Definitions ---

class PaymentStatus(BaseModel, SoftDeleteMixin):
    __tablename__ = 'payment_statuses'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)


class Order(BaseModel, SoftDeleteMixin):
    __tablename__ = 'orders'

    # --- Core Columns ---
    # Using UUID for consistency with other models
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    guest_email = db.Column(db.String(120), nullable=True) # For guest checkouts
    guest_phone = db.Column(db.String(20), nullable=True)

    # --- Status and Financials ---
    # Consolidated to a single status column using the Enum
    order_status = db.Column(db.Enum(OrderStatusEnum), nullable=False, default=OrderStatusEnum.PENDING)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)

    # --- Shipping and Tracking ---
    shipping_address_id = db.Column(UUID(as_uuid=True), db.ForeignKey('addresses.id'), nullable=False)
    billing_address_id = db.Column(UUID(as_uuid=True), db.ForeignKey('addresses.id'), nullable=True)
    tracking_number = db.Column(db.String(100))
    creator_ip_address = db.Column(db.String(45), nullable=True) # Removed duplicate definition

    # --- Relationships ---
    # Using foreign_keys to be explicit since multiple columns could link to User
    user = db.relationship('User', foreign_keys=[user_id], back_populates='orders')
    
    # Correct, single relationship definition for items
    items = db.relationship('OrderItem', back_populates='order', cascade="all, delete-orphan", lazy='dynamic')
    invoice = db.relationship('Invoice', back_populates='order', uselist=False, cascade="all, delete-orphan")

    def to_dict(self, view='user'):
        """
        Consolidated serialization method for an order.
        Provides different levels of detail based on the 'view' parameter.
        """
        data = {
            'id': str(self.id),
            'order_status': self.order_status.value,
            'total_amount': str(self.total_amount),
            'created_at': self.created_at.isoformat(),
            'tracking_number': self.tracking_number,
            'items': [item.to_dict() for item in self.items]
        }
        
        # Add more detailed user information for the admin view
        if view == 'admin' and self.user:
            data['user'] = {
                'id': str(self.user.id),
                'email': self.user.email,
                'full_name': self.user.full_name
            }
        elif self.guest_email:
            data['guest_email'] = self.guest_email

        return data

class OrderItem(BaseModel, SoftDeleteMixin):
    __tablename__ = 'order_items'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = db.Column(UUID(as_uuid=True), db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Numeric(10, 2), nullable=False)

    order = db.relationship('Order', back_populates='items')
    product = db.relationship('Product')

    def to_dict(self):
        return {
            'id': str(self.id),
            'product_id': str(self.product.id),
            'product_name': self.product.name,
            'quantity': self.quantity,
            'price_at_purchase': str(self.price_at_purchase)
        }

class Invoice(BaseModel, SoftDeleteMixin):
    __tablename__ = 'invoices'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = db.Column(UUID(as_uuid=True), db.ForeignKey('orders.id'), nullable=False, unique=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    pdf_url = db.Column(db.String(255)) # Renamed from pdf_path for clarity
    
    order = db.relationship('Order', back_populates='invoice')

    def to_dict(self):
        return {
            'id': str(self.id),
            'order_id': str(self.order_id),
            'invoice_number': self.invoice_number,
            'pdf_url': self.pdf_url,
            'created_at': self.created_at.isoformat()
        }