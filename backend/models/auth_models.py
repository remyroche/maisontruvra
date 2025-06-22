from backend.database import db
from .base import BaseModel

class TokenBlocklist(BaseModel):
    """
    Model for storing revoked JWT tokens.
    """
    __tablename__ = 'token_blocklist'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)
