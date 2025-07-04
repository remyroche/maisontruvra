# backend/models/loyalty_account.py

import uuid

from sqlalchemy.dialects.postgresql import UUID

from backend.extensions import db


class LoyaltyAccount(db.Model):
    __tablename__ = "loyalty_accounts"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False, unique=True
    )
    points_balance = db.Column(db.Integer, default=0)
    tier_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("loyalty_tiers.id"), nullable=True
    )

    user = db.relationship("User", back_populates="loyalty_account")
    tier = db.relationship("LoyaltyTier")
    transactions = db.relationship("LoyaltyTransaction", back_populates="account")

    def __repr__(self):
        return f"<LoyaltyAccount {self.user.username}>"
