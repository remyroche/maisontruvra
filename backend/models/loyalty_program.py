# backend/models/loyalty_program.py

import uuid

from sqlalchemy.dialects.postgresql import UUID

from backend.extensions import db


class LoyaltyProgram(db.Model):
    __tablename__ = "loyalty_programs"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)

    tiers = db.relationship(
        "LoyaltyTier", back_populates="program", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<LoyaltyProgram {self.name}>"
