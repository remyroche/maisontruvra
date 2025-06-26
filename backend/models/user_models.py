from .base import BaseModel, SoftDeleteMixin # Added: Import SoftDeleteMixin
from .enums import UserStatus, RoleType
from backend.database import db # Changed: Import db from backend.database
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from backend.utils.encryption import encrypt_data, decrypt_data # Changed: Use absolute import for utils
from argon2 import PasswordHasher
from backend.models.base import BaseModel # No change needed here
from backend.config import Config

ph = PasswordHasher()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    _email = db.Column('email', db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    _first_name = db.Column('first_name', db.String(50), nullable=False)
    _last_name = db.Column('last_name', db.String(50), nullable=False)
    _phone_number = db.Column('phone_number', db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_b2b = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    role = db.Column(db.String(80), default='user', nullable=False)
    language = db.Column(db.String(10), default='fr', nullable=False)

    addresses = db.relationship('Address', backref='user', lazy=True, cascade="all, delete-orphan")
    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    wishlist_items = db.relationship('WishlistItem', backref='user', lazy=True, cascade="all, delete-orphan")

    two_factor_secret = db.Column(db.String(255), nullable=True)
    two_factor_enabled = db.Column(db.Boolean, default=False)

    b2b_profile = db.relationship('B2BProfile', back_populates='user', uselist=False, cascade="all, delete-orphan")


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
        
    def set_password(self, password):
        self.password_hash = ph.hash(password)

    def check_password(self, password):
        try:
            return ph.verify(self.password_hash, password)
        except Exception:
            return False

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
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
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
    name = db.Column(db.Enum(RoleType), unique=True, nullable=False)

    users = db.relationship('User', secondary='user_roles', back_populates='roles')

    def to_dict(self):
        return {'id': self.id, 'name': self.name.value, 'is_deleted': self.is_deleted}


class UserRole(db.Model):
    __tablename__ = 'user_roles'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)

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
