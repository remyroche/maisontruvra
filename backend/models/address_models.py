from backend.database import db
from backend.models.base import BaseModel

class Address(BaseModel):
    """
    Represents a single shipping address associated with a user.
    """
    __tablename__ = 'addresses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Address details
    label = db.Column(db.String(100), nullable=False) # e.g., "Siège Social", "Entrepôt Principal"
    address_line_1 = db.Column(db.String(255), nullable=False)
    address_line_2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(255), nullable=True)
    contact_phone = db.Column(db.String(50), nullable=True)

    is_default = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "addressLine1": self.address_line_1,
            "addressLine2": self.address_line_2,
            "city": self.city,
            "postalCode": self.postal_code,
            "country": self.country,
            "contactPerson": self.contact_person,
            "contactPhone": self.contact_phone,
            "isDefault": self.is_default,
        }
