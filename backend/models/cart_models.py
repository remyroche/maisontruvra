from backend.models.base import Base
from backend.extensions import db

class Cart(Base):
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Can be null for guest carts
    discount_id = db.Column(db.Integer, db.ForeignKey('discounts.id'), nullable=True)

    user = db.relationship('User')
    items = db.relationship('CartItem', back_populates='cart', cascade="all, delete-orphan")
    discount = db.relationship('Discount')

class CartItem(Base):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    # This price field will store the standard product price or a custom price from a quote.
    price = db.Column(db.Numeric(10, 2), nullable=True)

    cart = db.relationship('Cart', back_populates='items')
    product = db.relationship('Product')


# Add the one-to-one relationship from User to Cart
from backend.models.user_models import User
User.cart = db.relationship('Cart', back_populates='user', uselist=False, cascade="all, delete-orphan")
