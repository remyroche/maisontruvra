from backend.database import db
from backend.models.base import BaseModel

class Cart(BaseModel):
    """
    Represents a user's shopping cart.
    """
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    items = db.relationship('CartItem', back_populates='cart', cascade="all, delete-orphan")
    user = db.relationship('User', back_populates='cart')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'items': [item.to_dict() for item in self.items]
        }

class CartItem(BaseModel):
    """
    Represents a single item within a shopping cart.
    """
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    cart = db.relationship('Cart', back_populates='items')
    product = db.relationship('Product')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'product_name': self.product.name,
            'price': self.product.price
        }

# Add the one-to-one relationship from User to Cart
from backend.models.user_models import User
User.cart = db.relationship('Cart', back_populates='user', uselist=False, cascade="all, delete-orphan")
