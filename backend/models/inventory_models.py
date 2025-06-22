from backend.database import db
from .base import BaseModel

class Inventory(BaseModel):
    __tablename__ = 'inventories'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, unique=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    
    product = db.relationship('Product', back_populates='inventory')

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'product_name': self.product.name,
            'sku': self.product.sku,
            'quantity': self.quantity
        }
