from backend.database import db
from backend.models.base import BaseModel
from backend.models.user_models import User


class Cart(BaseModel):
    __tablename__ = "carts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    
    # Relationships
    user = db.relationship("User", back_populates="cart")
    items = db.relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Cart {self.id} for User {self.user_id}>"


class CartItem(BaseModel):
    __tablename__ = "cart_items"
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey("carts.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    
    # Relationships
    cart = db.relationship("Cart", back_populates="items")
    product = db.relationship("Product")

    def __repr__(self):
        return f"<CartItem {self.id} (Product {self.product_id}, Qty {self.quantity})>"

# Add the one-to-one relationship from User to Cart
User.cart = db.relationship(
    "Cart", back_populates="user", uselist=False, cascade="all, delete-orphan"
)
