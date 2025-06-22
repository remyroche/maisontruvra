from backend.database import db
from .base import BaseModel

class AuditLog(BaseModel):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    
    user = db.relationship('User')

    def to_dict(self):
        return {
            "id": self.id,
            "user_email": self.user.email if self.user else "System",
            "action": self.action,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }
