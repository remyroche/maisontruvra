from backend.database import db
from .base import BaseModel
import uuid

class ProductPassport(BaseModel):
    __tablename__ = 'product_passports'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    product = db.relationship('Product', back_populates='passport')
    entries = db.relationship('PassportEntry', back_populates='passport', cascade="all, delete-orphan", order_by="PassportEntry.timestamp")

    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product.name,
            'created_at': self.created_at.isoformat()
        }
    
    def to_dict_detailed(self):
        data = self.to_dict()
        data['entries'] = [entry.to_dict() for entry in self.entries]
        return data

class PassportEntry(BaseModel):
    __tablename__ = 'passport_entries'
    id = db.Column(db.Integer, primary_key=True)
    passport_id = db.Column(db.String(36), db.ForeignKey('product_passports.id'), nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, nullable=False)
    
    passport = db.relationship('ProductPassport', back_populates='entries')
    
    def to_dict(self):
        return {
            'event_type': self.event_type,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }