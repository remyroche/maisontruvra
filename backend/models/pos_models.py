import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy.dialects.postgresql import UUID

from .. import db
from .base import BaseModel


class POSTransaction(BaseModel):
    """Model for POS transactions."""
    
    __tablename__ = "pos_transactions"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = db.Column(db.String(50), unique=True, nullable=False)
    order_id = db.Column(UUID(as_uuid=True), db.ForeignKey("orders.id"), nullable=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=True)
    
    # Transaction details
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # cash, card, etc.
    payment_reference = db.Column(db.String(100), nullable=True)
    
    # Status tracking
    status = db.Column(db.String(20), default="pending")  # pending, completed, voided, failed
    processed_at = db.Column(db.DateTime, nullable=True)
    voided_at = db.Column(db.DateTime, nullable=True)
    void_reason = db.Column(db.String(255), nullable=True)
    
    # POS terminal info
    terminal_id = db.Column(db.String(50), nullable=True)
    cashier_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=True)
    
    # Relationships
    order = db.relationship("Order", foreign_keys=[order_id])
    user = db.relationship("User", foreign_keys=[user_id])
    cashier = db.relationship("User", foreign_keys=[cashier_id])
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "transaction_id": self.transaction_id,
            "order_id": str(self.order_id) if self.order_id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "total_amount": str(self.total_amount),
            "payment_method": self.payment_method,
            "payment_reference": self.payment_reference,
            "status": self.status,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "voided_at": self.voided_at.isoformat() if self.voided_at else None,
            "void_reason": self.void_reason,
            "terminal_id": self.terminal_id,
            "cashier_id": str(self.cashier_id) if self.cashier_id else None,
            "created_at": self.created_at.isoformat(),
        }