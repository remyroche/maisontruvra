from backend.database import db
from .base import BaseModel
from .enums import UserStatus, RoleType
from werkzeug.security import generate_password_hash, check_password_hash

class User(BaseModel):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    status = db.Column(db.Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    mfa_secret = db.Column(db.String(16), nullable=True)
    mfa_enabled = db.Column(db.Boolean, default=False)
    
    roles = db.relationship('Role', secondary='user_roles', back_populates='users')
    addresses = db.relationship('Address', back_populates='user', cascade="all, delete-orphan")
    orders = db.relationship('Order', back_populates='user')
    cart = db.relationship('Cart', back_populates='user', uselist=False, cascade="all, delete-orphan")
    b2b_account = db.relationship('B2BUser', back_populates='user', cascade="all, delete-orphan")

    # --- New fields for Loyalty Program ---
    last_active_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    loyalty_tier_id = db.Column(db.Integer, db.ForeignKey('loyalty_tiers.id'), nullable=True)

    loyalty_tier = db.relationship('LoyaltyTier', back_populates='users')
    
        
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'roles': [role.name.value for role in self.roles]
            data['loyalty_tier'] = self.loyalty_tier.name if self.loyalty_tier else None
            data['last_active_at'] = self.last_active_at.isoformat() if self.last_active_at else None
        }
    
    def to_dict_admin(self):
        data = self.to_dict()
        data['status'] = self.status.value
        data['mfa_enabled'] = self.mfa_enabled
        data['created_at'] = self.created_at.isoformat()
        return data

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
