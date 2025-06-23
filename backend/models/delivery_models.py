from backend.database import db
from backend.models.base import BaseModel

# Association table for the many-to-many relationship
delivery_tier_association = db.Table('delivery_tier_association',
    db.Column('delivery_method_id', db.Integer, db.ForeignKey('delivery_methods.id'), primary_key=True),
    db.Column('loyalty_tier_id', db.Integer, db.ForeignKey('loyalty_tiers.id'), primary_key=True)
)

class DeliveryMethod(BaseModel):
    """
    Represents a delivery option that an admin can create and configure.
    """
    __tablename__ = 'delivery_methods'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float, nullable=False, default=0.0)

    # Many-to-many relationship with LoyaltyTier
    # This determines which tiers can see and use this delivery method.
    accessible_to_tiers = db.relationship(
        'LoyaltyTier', 
        secondary=delivery_tier_association,
        backref=db.backref('delivery_methods', lazy='dynamic')
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'accessible_to_tiers': [tier.name for tier in self.accessible_to_tiers]
        }
