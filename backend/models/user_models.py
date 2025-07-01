from .base import Base, db, SoftDeleteMixin, BaseModel
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from .enums import UserType, UserStatus, NotificationFrequency, RoleType
import datetime
from backend.utils.encryption import decrypt_data, encrypt_data
from sqlalchemy.ext.hybrid import hybrid_property

class User(Base):
    """
    Represents a user of the application.
    This model stores authentication details and personal information for both B2C and B2B customers.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    
    # User Type and Status
    user_type = Column(SQLAlchemyEnum(UserType), default=UserType.B2C)
    status = Column(SQLAlchemyEnum(UserStatus), default=UserStatus.PENDING_VERIFICATION)

    # Timestamps and Tracking
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    last_login_at = Column(DateTime)
    
    # Preferences
    notification_frequency = Column(SQLAlchemyEnum(NotificationFrequency), default=NotificationFrequency.INSTANT)
    
    # Security Features
    is_2fa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(100))
    
    # Relationships
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    orders = db.relationship('Order', backref='user', lazy=True)
    roles = db.relationship('Role', secondary='user_roles', back_populates='users')
    loyalty_account = db.relationship('UserLoyalty', back_populates='user', uselist=False)
    referrals_made = db.relationship('Referral', foreign_keys='Referral.referrer_id', back_populates='referrer')
    carts = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    wishlists = relationship("Wishlist", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user")
    
    # B2B specific relationship - one-to-one
    b2b_user = relationship("B2BUser", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    # Passport relationship
    passport = relationship("ProductPassport", back_populates="owner", uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

    @property
    def is_staff(self):
        """A user is considered staff if they have any role."""
        return len(self.roles) > 0

    @property
    def is_admin(self):
        """A user is an admin if they have the 'Admin' role."""
        return any(role.name == 'Admin' for role in self.roles)

    def get_permissions(self):
        """Returns a set of all permissions for the user from all their roles."""
        perms = set()
        for role in self.roles:
            for permission in role.permissions:
                perms.add(permission.name)
        return perms
        

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
        return decrypt_data(self._phone_number)

    @phone_number.setter
    def phone_number(self, value):
        self._phone_number = encrypt_data(value)

    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def to_public_dict(self):
        """Serialization for public-facing contexts (e.g., product reviews)."""
        return {
            'id': self.id,
            'first_name': self.first_name,
        }

    def to_user_dict(self):
        """Serialization for the user viewing their own profile."""
        data = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'is_b2b': self.is_b2b,
            'two_factor_enabled': self.two_factor_enabled
        }
        if self.is_b2b and self.b2b_profile:
            data['b2b_profile'] = self.b2b_profile.to_dict()
        return data

    def to_admin_dict(self):
        """Serialization for admins viewing user profiles."""
        data = self.to_user_dict()
        data.update({
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_mfa_enabled': self.is_mfa_enabled,
            'is_email_verified': self.is_email_verified,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'loyalty_info': self.loyalty.to_dict() if self.loyalty else None,
            'orders': [order.to_admin_dict() for order in self.orders],
            'addresses': [address.to_dict() for address in self.addresses]
        })
        return data

    def to_dict(self, view='user'):
        """Default to_dict that routes to the appropriate view."""
        if view == 'admin':
            return self.to_admin_dict()
        elif view == 'public':
            return self.to_public_dict()
        return self.to_user_dict()


class Role(BaseModel, SoftDeleteMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    users = db.relationship('User', secondary='user_roles', back_populates='roles')

    def to_dict(self):
        return {'id': self.id, 'name': self.name.value, 'is_deleted': self.is_deleted}


class UserRole(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

class Address(BaseModel, SoftDeleteMixin):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    address_line_1 = db.Column(db.String(255), nullable=False)
    address_line_2 = db.Column(db.String(255))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)

    user = db.relationship('User', back_populates='addresses')

    def to_dict(self):
        return {
            'id': self.id,
            'address_line_1': self.address_line_1,
            'address_line_2': self.address_line_2,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country,
            'is_deleted': self.is_deleted,
        }
