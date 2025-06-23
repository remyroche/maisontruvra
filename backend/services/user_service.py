from models import db, User, Address, Role
from sqlalchemy.orm import joinedload, subqueryload
from werkzeug.security import generate_password_hash, check_password_hash
from utils.auth_helpers import send_password_reset_email
from argon2 import PasswordHasher
from utils.encryption import encrypt_data

ph = PasswordHasher()

class UserService:
    def get_all_users_paginated(self, page, per_page, role=None, search_term=None):
        """
        Gets a paginated list of users, eagerly loading relationships
        to prevent N+1 query problems.
        """
        query = User.query.options(
            joinedload(User.addresses),
            subqueryload(User.orders) # Use subqueryload for collections to avoid cartesian product
        )
        
        if role:
            query = query.filter(User.roles.any(name=role))
        if search_term:
            # Note: Searching encrypted fields with ILIKE is not efficient and 
            # might not work depending on the database. For production, consider
            # a different approach for searching encrypted data.
            search_term_encrypted = encrypt_data(f"%{search_term}%")
            query = query.filter(User._email.ilike(search_term_encrypted) | User._first_name.ilike(search_term_encrypted) | User._last_name.ilike(search_term_encrypted))
            
        return query.order_by(User.id).paginate(page=page, per_page=per_page, error_out=False)

    def get_user_by_id(self, user_id):
        """
        Gets a single user by ID, eagerly loading relationships.
        """
        return User.query.options(
            joinedload(User.addresses),
            subqueryload(User.orders)
        ).get(user_id)

    def create_user(self, data, by_admin=False):
        email = data.get('email')
        if User.query.filter_by(_email=encrypt_data(email)).first():
            raise ValueError('Email address already registered.')
        
        user = User(
            email=email,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone_number=data.get('phone_number')
        )
        user.set_password(data.get('password'))

        if by_admin:
            user.is_admin = data.get('is_admin', False)
        
        db.session.add(user)
        db.session.commit()
        return user

    def update_user(self, user_id, data, by_admin=False):
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        if 'email' in data:
            user.email = data['email']
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'phone_number' in data:
            user.phone_number = data['phone_number']

        if by_admin:
            if 'is_admin' in data:
                user.is_admin = data['is_admin']
            if 'is_active' in data:
                user.is_active = data['is_active']
        
        db.session.commit()
        return user
    
    def update_password(self, user_id, new_password):
        user = self.get_user_by_id(user_id)
        user.set_password(new_password)
        db.session.commit()

    def get_user_by_email(self, email):
        return User.query.filter_by(_email=encrypt_data(email)).first()
        
    def authenticate_user(self, email, password):
        user = self.get_user_by_email(email)
        if user and user.check_password(password):
            return user
        return None
    
    def authenticate_staff_or_admin(self, email, password):
        user = self.get_user_by_email(email)
        if user and user.check_password(password) and user.is_staff():
            return user
        return None

    def delete_user(self, user_id):
        user = self.get_user_by_id(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False

    def add_address(self, user_id, data):
        address = Address(user_id=user_id, **data)
        db.session.add(address)
        db.session.commit()
        return address

    def update_address(self, address_id, data, user_id):
        address = Address.query.filter_by(id=address_id, user_id=user_id).first_or_404()
        for key, value in data.items():
            setattr(address, key, value)
        db.session.commit()
        return address

    def delete_address(self, address_id, user_id):
        address = Address.query.filter_by(id=address_id, user_id=user_id).first_or_404()
        db.session.delete(address)
        db.session.commit()

    def initiate_password_reset(self, email):
        user = self.get_user_by_email(email)
        if user:
            # In a real app, generate a secure token and its expiration
            token = "some-secure-token" # Replace with actual token generation
            send_password_reset_email(user.email, token)

    def reset_password(self, token, new_password):
        # In a real app, validate the token and find the user
        user = User.query.first() # Replace with actual user lookup from token
        if user:
            user.set_password(new_password)
            db.session.commit()
            return True
        return False
    
    def get_all_roles(self):
        return Role.query.all()

    def update_user_roles(self, user_id, role_ids):
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        roles = Role.query.filter(Role.id.in_(role_ids)).all()
        user.roles = roles
        db.session.commit()
        return user
    
    def update_password(self, user_id, new_password):
        user = self.get_user_by_id(user_id)
        user.set_password(new_password)
        db.session.commit()

        
    def authenticate_user(self, email, password):
        user = self.get_user_by_email(email)
        if user and user.check_password(password):
            return user
        return None
    
    def authenticate_admin(self, email, password):
        user = self.get_user_by_email(email)
        if user and user.check_password(password) and user.is_admin:
            return user
        return None

    def delete_user(self, user_id):
        user = self.get_user_by_id(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False

    def add_address(self, user_id, data):
        address = Address(user_id=user_id, **data)
        db.session.add(address)
        db.session.commit()
        return address
        
    def get_all_users_paginated(self, page, per_page, role=None, search_term=None):
        query = User.query
        if role:
            query = query.filter(User.roles.any(name=role))
        if search_term:
            search_term_encrypted = encrypt_data(f"%{search_term}%")
            query = query.filter(User._email.ilike(search_term_encrypted) | User._first_name.ilike(search_term_encrypted) | User._last_name.ilike(search_term_encrypted))
        return query.paginate(page=page, per_page=per_page, error_out=False)
    

        
        roles = Role.query.filter(Role.id.in_(role_ids)).all()
        user.roles = roles
        db.session.commit()
        return user
from backend.models.user_models import User, UserRole
from backend.database import db
from backend.services.exceptions import NotFoundException, ValidationException
from sqlalchemy.orm import joinedload
import logging

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    def get_user_by_id(user_id, include_sensitive=False):
        """Get user by ID with optional sensitive data."""
        user = User.query.get(user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")
        return user
        
    @staticmethod
    def get_users_list(page=1, per_page=20, role=None):
        """Get paginated list of users with optimized queries."""
        query = User.query.options(joinedload(User.loyalty_tier))
        
        if role:
            query = query.filter(User.role == role)
            
        users = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return {
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        }
        
    @staticmethod
    def update_user(user_id, data, admin_id=None):
        """Update user data with audit logging."""
        user = UserService.get_user_by_id(user_id)
        
        # Validate and update fields
        if 'email' in data:
            email = data['email'].strip().lower()
            existing = User.query.filter(User.email == email, User.id != user_id).first()
            if existing:
                raise ValidationException("Email already in use")
            user.email = email
            
        if 'role' in data:
            try:
                user.role = UserRole(data['role'])
            except ValueError:
                raise ValidationException("Invalid role")
                
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
            
        db.session.commit()
        
        # Log admin action
        if admin_id:
            logger.info(f"Admin {admin_id} updated user {user_id}: {list(data.keys())}")
            
        return user
        
    @staticmethod
    def deactivate_user(user_id, admin_id=None):
        """Deactivate a user account."""
        user = UserService.get_user_by_id(user_id)
        user.is_active = False
        db.session.commit()
        
        if admin_id:
            logger.info(f"Admin {admin_id} deactivated user {user_id}")
            
        return user
