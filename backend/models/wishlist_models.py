# backend/models/wishlist_models.py

from .base import db


class Wishlist(db.Model):
    """
    Represents a user's wishlist. Each user has one wishlist.
    """

    __tablename__ = "wishlists"

    id = db.Column(db.Integer, primary_key=True)
    # A user can only have one wishlist, so this should be unique.
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False
    )

    # The 'items' relationship will load all wishlist items for a given wishlist.
    # 'cascade="all, delete-orphan"' ensures that when a wishlist is deleted,
    # all its associated items are also deleted.
    items = db.relationship(
        "WishlistItem", backref="wishlist", lazy="dynamic", cascade="all, delete-orphan"
    )

    def to_dict(self):
        """Serializes the Wishlist object to a dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "items": [item.to_dict() for item in self.items],
        }


class WishlistItem(db.Model):
    """
    Represents a single product item within a user's wishlist.
    """

    __tablename__ = "wishlist_items"

    id = db.Column(db.Integer, primary_key=True)
    wishlist_id = db.Column(db.Integer, db.ForeignKey("wishlists.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    added_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationship to get product details easily from a WishlistItem
    product = db.relationship("Product")

    def to_dict(self):
        """Serializes the WishlistItem object to a dictionary."""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name,
            "product_image_url": self.product.image_url,
            "product_price": self.product.price,
            "added_at": self.added_at.isoformat(),
        }
