import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID

from backend.database import db


class AdminAuditLog(db.Model):
    __tablename__ = "admin_audit_log"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    action = db.Column(db.String(255), nullable=False, index=True)
    staff_log_id = db.Column(
        UUID(as_uuid=False),
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
    )

    # What kind of object was affected? e.g., "Product", "User"
    target_type = db.Column(db.String(100), nullable=True)
    # The ID of the affected object
    target_id = db.Column(db.Integer, nullable=True, index=True)

    # Detailed information about the change (e.g., before/after states)
    details = db.Column(db.JSON, nullable=True)

    # Security information
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Renamed from 'admin' to 'user' for consistency with the old model
    user = db.relationship("User", backref="admin_audit_logs")

    def to_dict(self):
        """Serializes the object to a dictionary."""
        return {
            "id": self.id,
            "staff_log_id": self.staff_log_id,
            "timestamp": self.timestamp.isoformat(),
            "userEmail": self.user.email if self.user else "Utilisateur inconnu",
            "action": self.action,
            "targetType": self.target_type,
            "targetId": self.target_id,
            "details": self.details,
            "ipAddress": self.ip_address,
        }

    def __repr__(self):
        return f"<AdminAuditLog {self.id} by User {self.user_id}>"
