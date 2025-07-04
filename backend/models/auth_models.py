from backend.database import db
from .base import BaseModel
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import (
    JSON,
)

# Association table for AdminUser and Role
admin_user_roles = db.Table(
    "admin_user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("admin_user.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id"), primary_key=True),
)


class AdminUser(db.Model):
    __tablename__ = "admin_user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)

    # Relationship to roles
    roles = db.relationship("Role", secondary=admin_user_roles, back_populates="users")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def permissions(self):
        """Returns a set of all permissions for the user based on their roles."""
        all_perms = set()
        for role in self.roles:
            all_perms.update(role.permissions)
        return all_perms

    def has_permission(self, permission):
        """Checks if the user has a specific permission."""
        return permission in self.permissions


class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

    # Store permissions as a JSON array
    permissions = db.Column(JSON, nullable=False, default=[])

    users = db.relationship(
        "AdminUser", secondary=admin_user_roles, back_populates="roles"
    )

    def __repr__(self):
        return f"<Role {self.name}>"


class TokenBlocklist(BaseModel):
    """
    Model for storing revoked JWT tokens.
    """

    __tablename__ = "token_blocklist"
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)
