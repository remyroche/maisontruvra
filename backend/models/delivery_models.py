from sqlalchemy.orm import relationship

from backend.extensions import db

from .base import BaseModel

# Association table for the many-to-many relationship
# between countries and delivery options.
country_delivery_options = db.Table(
    "country_delivery_options",
    db.Column(
        "country_id", db.Integer, db.ForeignKey("countries.id"), primary_key=True
    ),
    db.Column(
        "delivery_option_id",
        db.Integer,
        db.ForeignKey("delivery_options.id"),
        primary_key=True,
    ),
)

# Association table for Delivery Options and B2B Tiers
delivery_option_b2b_tiers = db.Table(
    "delivery_option_b2b_tiers",
    db.Column(
        "delivery_option_id",
        db.Integer,
        db.ForeignKey("delivery_options.id"),
        primary_key=True,
    ),
    db.Column(
        "b2b_tier_id", db.Integer, db.ForeignKey("b2b_tiers.id"), primary_key=True
    ),
)


class Country(BaseModel):
    """Model for storing countries we deliver to."""

    __tablename__ = "countries"

    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(2), unique=True, nullable=False)  # ISO 3166-1 alpha-2
    is_active = db.Column(db.Boolean, default=False, nullable=False)

    delivery_options = relationship(
        "DeliveryOption",
        secondary=country_delivery_options,
        back_populates="available_in_countries",
    )

    def __repr__(self):
        return f"<Country {self.name}>"


class DeliveryOption(BaseModel):
    __tablename__ = "delivery_options"

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    available_in_countries = relationship(
        "Country", secondary=country_delivery_options, back_populates="delivery_options"
    )

    # Relationship to B2B Tiers to restrict a delivery option to specific customer tiers.
    accessible_to_tiers = relationship(
        "B2BTier",
        secondary=delivery_option_b2b_tiers,
        back_populates="available_delivery_options",
    )

    def to_dict(self):
        """Helper method to convert model instance to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": str(self.price),
            "is_active": self.is_active,
            "accessible_to_tiers": [tier.name for tier in self.accessible_to_tiers],
        }

    def __repr__(self):
        return f"<DeliveryOption {self.name}>"
