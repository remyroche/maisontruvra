from backend.database import db
from backend.models.base import BaseModel

class AuditLog(BaseModel):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action = db.Column(db.String(255), nullable=False, index=True)
    target_id = db.Column(db.Integer, nullable=True, index=True)
    details = db.Column(db.JSON, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True) # For IPv4 and IPv6

    user = db.relationship('User', backref='audit_logs')

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.created_at.isoformat(),
            'userEmail': self.user.email if self.user else 'Utilisateur inconnu',
            'action': self.action,
            'targetId': self.target_id,
            'details': self.details,
            'ipAddress': self.ip_address,
        }
