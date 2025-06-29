import enum
from sqlalchemy import Column, String, Boolean, Enum as SQLAlchemyEnum
from backend.database import db
from .base import BaseModel


class NewsletterType(enum.Enum):
    B2C = "b2c"
    B2B = "b2b"

class NewsletterSubscriber(BaseModel):
    """Stores email addresses of users who subscribed to the newsletter."""
    __tablename__ = 'newsletter_subscribers'

    # id, created_at, and updated_at are inherited from BaseModel
    
    email = db.Column(String(255), unique=True, nullable=False)
    # New field to distinguish between newsletter lists
    list_type = db.Column(SQLAlchemyEnum(NewsletterType), nullable=False, default=NewsletterType.B2C)
    is_active = db.Column(Boolean, default=True)

    def __repr__(self):
        return f'<NewsletterSubscriber {self.email}>'

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'list_type': self.list_type.value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }