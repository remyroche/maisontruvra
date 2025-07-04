from backend.extensions import db
from backend.models.base import BaseModel


class Cart(BaseModel):
    __tablename__ = "carts"
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )  # Can be null for guest carts
    discount_id = db.Column(db.Integer, db.ForeignKey("discounts.id"), nullable=True)

    user = db.relationship("User")
    items = db.relationship(
        "CartItem", back_populates="cart", cascade="all, delete-orphan"
    )
    discount = db.relationship("Discount")


class CartItem(BaseModel):
    __tablename__ = "cart_items"
    cart_id = db.Column(db.Integer, db.ForeignKey("carts.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    # This price field will store the standard product price or a custom price from a quote.
    price = db.Column(db.Numeric(10, 2), nullable=True)

    cart = db.relationship("Cart", back_populates="items")
    product = db.relationship("Product")


# Add the one-to-one relationship from User to Cart
from backend.models.user_models import User

User.cart = db.relationship(
    "Cart", back_populates="user", uselist=False, cascade="all, delete-orphan"
)
