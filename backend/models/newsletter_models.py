from backend.database import db
from backend.models.base import BaseModel
import enum

class NewsletterType(enum.Enum):
    B2C = "b2c"
    B2B = "b2b"

class NewsletterSubscriber(BaseModel):
    __tablename__ = 'newsletter_subscribers'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    # New field to distinguish between newsletter lists
    list_type = db.Column(db.Enum(NewsletterType), nullable=False, default=NewsletterType.B2C)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'list_type': self.list_type.value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
