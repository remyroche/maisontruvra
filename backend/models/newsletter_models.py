from backend.database import db
from .base import BaseModel

class NewsletterSubscription(BaseModel):
    __tablename__ = 'newsletter_subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_b2b = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'is_b2b': self.is_b2b,
            'subscribed_at': self.created_at.isoformat()
        }
