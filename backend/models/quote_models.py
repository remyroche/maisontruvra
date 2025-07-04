from backend.models.base import BaseModel
from backend.extensions import db
from datetime import datetime, timedelta


class Quote(BaseModel):
    __tablename__ = "quotes"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(
        db.String(50), default="pending"
    )  # pending, responded, accepted, expired
    responded_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User")
    items = db.relationship(
        "QuoteItem", back_populates="quote", cascade="all, delete-orphan"
    )

    def set_expiry(self, days=7):
        self.expires_at = datetime.utcnow() + timedelta(days=days)


class QuoteItem(BaseModel):
    __tablename__ = "quote_items"
    quote_id = db.Column(db.Integer, db.ForeignKey("quotes.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    response_price = db.Column(
        db.Numeric(10, 2), nullable=True
    )  # Price offered by admin

    quote = db.relationship("Quote", back_populates="items")
    product = db.relationship("Product")
