from backend.database import db
from .base import BaseModel
from .enums import UserStatus, RoleType
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from utils.encryption import encrypt_data, decrypt_data
from argon2 import PasswordHasher

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
    
    addresses = db.relationship('Address', backref='user', lazy=True, cascade="all, delete-orphan")
    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    wishlist_items = db.relationship('WishlistItem', backref='user', lazy=True, cascade="all, delete-orphan")
    
    two_factor_secret = db.Column(db.String(255), nullable=True)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    
    b2b_profile = db.relationship('B2BProfile', back_populates='user', uselist=False, cascade="all, delete-orphan")

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

    @validates('addresses')
    def validate_addresses(self, key, address):
        """
        Enforces the business rule that a user cannot have more than 4 addresses.
        """
        if len(self.addresses.all()) >= 4:
            raise ValueError("Un utilisateur ne peut pas avoir plus de 4 adresses.")
        return address

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict_admin(self):
        data = self.to_dict()
        data['status'] = self.status.value
        data['mfa_enabled'] = self.mfa_enabled
        data['created_at'] = self.created_at.isoformat()
        return data

    def to_dict(self, include_orders=False, include_addresses=False, include_b2b=False):
        user_dict = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'is_admin': self.is_admin,
            'is_b2b': self.is_b2b,
            'two_factor_enabled': self.two_factor_enabled
        }
        if include_orders:
            user_dict['orders'] = [order.to_dict() for order in self.orders]
        if include_addresses:
            user_dict['addresses'] = [address.to_dict() for address in self.addresses]
        if include_b2b and self.b2b_profile:
            user_dict['b2b_profile'] = self.b2b_profile.to_dict()
        return user_dict

class Role(BaseModel):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Enum(RoleType), unique=True, nullable=False)
    
    users = db.relationship('User', secondary='user_roles', back_populates='roles')

    def to_dict(self):
        return {'id': self.id, 'name': self.name.value}

class UserRole(db.Model):
    __tablename__ = 'user_roles'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)

class Address(BaseModel):
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
        }
