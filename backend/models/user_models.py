import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLAlchemyEnum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from backend.extensions import db
from backend.utils.encryption import decrypt_data, encrypt_data

from .base import BaseModel, SoftDeleteMixin
from .enums import NotificationFrequency, RoleType, UserStatus, UserType


class User(BaseModel, SoftDeleteMixin):
    """
    Represents a user of the application, storing authentication, personal,
    and relational data for all user types (B2C, B2B, Staff).
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    # Encrypted fields are stored in columns with a leading underscore.
    # The hybrid properties below provide transparent access.
    _first_name = Column("first_name", String(256), nullable=False)
    _last_name = Column("last_name", String(256), nullable=False)
    _email = Column("email", String(256), unique=True, nullable=False)
    _phone_number = Column("phone_number", String(256), nullable=True)

    password_hash = Column(String(256), nullable=False)
    is_active = Column(Boolean, default=True)
    is_guest = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime)

    # User Type and Status
    status = Column(SQLAlchemyEnum(UserStatus), default=UserStatus.PENDING_VERIFICATION)
    user_type = Column(SQLAlchemyEnum(UserType), default=UserType.B2C, nullable=False)

    # B2B Specific Fields
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    company = relationship("Company", back_populates="users")
    b2b_status = Column(String(50), default="none") # Legacy, consider moving to B2BAccount model

    # Preferences
    notification_frequency = Column(
        SQLAlchemyEnum(NotificationFrequency), default=NotificationFrequency.INSTANT
    )

    # Security Features
    is_2fa_enabled = Column(Boolean, default=False)
    totp_secret = Column(String(100), nullable=True)
    is_magic_link_enabled = Column(Boolean, default=False)
    magic_link_token = Column(String(255), nullable=True)
    magic_link_expires_at = Column(DateTime, nullable=True)

    # Relationships
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", backref="user", lazy=True)
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    loyalty_account = relationship("UserLoyalty", back_populates="user", uselist=False)
    cart = relationship("Cart", back_populates="user", uselist=False, cascade="all, delete-orphan")
    wishlist = relationship("Wishlist", back_populates="user", uselist=False, cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user")
    b2b_profile = relationship("B2BAccount", back_populates="user", uselist=False)
    passport = relationship("ProductPassport", back_populates="owner", uselist=False)
    
    # Referral Program Fields
    referral_code = Column(String(20), unique=True, nullable=True)
    referred_by_id = Column("referred_by", Integer, ForeignKey("users.id"), nullable=True)
    referrals_made = relationship("Referral", foreign_keys="Referral.referrer_id", back_populates="referrer")

    # --- Hybrid Properties for Encrypted Fields ---
    @hybrid_property
    def email(self):
        return decrypt_data(self._email)

    @email.setter
    def email(self, value):
        self._email = encrypt_data(value)

    @hybrid_property
    def first_name(self):
        return decrypt_data(self._first_name)

    @first_name.setter
    def first_name(self, value):
        self._first_name = encrypt_data(value)

    @hybrid_property
    def last_name(self):
        return decrypt_data(self._last_name)

    @last_name.setter
    def last_name(self, value):
        self._last_name = encrypt_data(value)

    @hybrid_property
    def phone_number(self):
        return decrypt_data(self._phone_number) if self._phone_number else None

    @phone_number.setter
    def phone_number(self, value):
        self._phone_number = encrypt_data(value) if value else None

    # --- Other Properties ---
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_staff(self):
        return any(role.name in [RoleType.ADMIN, RoleType.STAFF, RoleType.MANAGER] for role in self.roles)

    @property
    def is_admin(self):
        return any(role.name == RoleType.ADMIN for role in self.roles)
        
    @property
    def is_b2b(self):
        return self.user_type == UserType.B2B

    # --- Methods ---
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_permissions(self):
        return {perm.name for role in self.roles for perm in role.permissions}

    # --- Serialization ---
    def to_dict(self, view="user"):
        if view == "admin":
            return self.to_admin_dict()
        if view == "public":
            return self.to_public_dict()
        return self.to_user_dict()

    def to_public_dict(self):
        return {"id": self.id, "first_name": self.first_name}

    def to_user_dict(self):
        return {
            "id": self.id, "email": self.email, "first_name": self.first_name,
            "last_name": self.last_name, "phone_number": self.phone_number,
            "is_b2b": self.is_b2b, "is_2fa_enabled": self.is_2fa_enabled,
            "b2b_profile": self.b2b_profile.to_dict() if self.is_b2b and self.b2b_profile else None
        }

    def to_admin_dict(self):
        data = self.to_user_dict()
        data.update({
            "is_email_verified": self.email_verified_at is not None,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat(),
            "loyalty_info": self.loyalty_account.to_dict() if self.loyalty_account else None,
            "orders": [order.to_admin_dict() for order in self.orders],
            "addresses": [address.to_dict() for address in self.addresses],
        })
        return data

    def __repr__(self):
        return f"<User {self.id}: {self.email}>"


class Role(BaseModel, SoftDeleteMixin):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(SQLAlchemyEnum(RoleType), unique=True, nullable=False)
    users = relationship("User", secondary="user_roles", back_populates="roles")

    def to_dict(self):
        return {"id": self.id, "name": self.name.value, "is_deleted": self.is_deleted}


class UserRole(db.Model):
    __tablename__ = "user_roles"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)


class Address(BaseModel, SoftDeleteMixin):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    address_line_1 = Column(String(255), nullable=False)
    address_line_2 = Column(String(255))
    city = Column(String(100), nullable=False)
    state = Column(String(100))
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)
    user = relationship("User", back_populates="addresses")

    def to_dict(self):
        return {
            "id": self.id, "address_line_1": self.address_line_1,
            "address_line_2": self.address_line_2, "city": self.city,
            "state": self.state, "postal_code": self.postal_code,
            "country": self.country, "is_deleted": self.is_deleted,
        }
