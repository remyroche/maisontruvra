from backend.database import db
from .base import BaseModel
from sqlalchemy.dialects.postgresql import JSONB


class GenericRequest(BaseModel):
    """
    A model to handle various types of requests like quotes, information, etc.
    """

    __tablename__ = "generic_requests"
    id = db.Column(db.Integer, primary_key=True)
    request_type = db.Column(
        db.String(50), nullable=False
    )  # e.g., 'quote', 'info', 'support'
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    details = db.Column(JSONB)  # Store form data as JSON
    status = db.Column(db.String(50), default="new")  # new, in_progress, resolved

    user = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "request_type": self.request_type,
            "user_email": self.user.email
            if self.user
            else self.details.get("email", "N/A"),
            "details": self.details,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }
