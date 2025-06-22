from backend.database import db
from .base import BaseModel
from sqlalchemy.dialects.postgresql import JSONB

class Setting(BaseModel):
    """
    A simple key-value store for site-wide settings.
    """
    __tablename__ = 'settings'
    # Use key as primary key instead of auto-incrementing id
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(JSONB) # Use JSONB to store various types of values

    # Override the default id from BaseModel
    id = None 

    def to_dict(self):
        return {
            'key': self.key,
            'value': self.value
        }
