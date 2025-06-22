from backend.models import User, Role, RoleType, B2BUser
from backend.database import db
from backend.services.exceptions import ServiceException, NotFoundException, ValidationException
from backend.services.rbac_service import RBACService
import re
import random
import string

class UserService:

    @staticmethod
    def is_password_strong(password):
        """Checks if a password meets complexity requirements."""
        if len(password) < 8:
            return False
        if not re.search("[a-z]", password):
            return False
        if not re.search("[A-Z]", password):
            return False
        if not re.search("[0-9]", password):
            return False
        return True

    @staticmethod
    def generate_temporary_password(length=12):
        """Generates a random, secure password for temporary use."""
        characters = string.ascii_letters + string.digits
        password = ''.join(random.choice(characters) for i in range(length))
        # Ensure it meets complexity by adding one of each required type if missing
        if not re.search("[a-z]", password): password += 'a'
        if not re.search("[A-Z]", password): password += 'B'
        if not re.search("[0-9]", password): password += '1'
        return password

    @staticmethod
    def create_user(data, assign_default_role=True):
        """Creates a new user and assigns roles."""
        if User.query.filter_by(email=data['email']).first():
            raise ValidationException("Email address already in use.")
            
        if not UserService.is_password_strong(data['password']):
            raise ValidationException("Password is not strong enough.")

        user = User(
            email=data['email'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush() # Flush to get the user ID for role assignment
        
        # Assign roles
        if 'role_names' in data and data['role_names']:
            for role_name in data['role_names']:
                RBACService.assign_role_to_user(user.id, role_name)
        elif assign_default_role:
             RBACService.assign_role_to_user(user.id, RoleType.B2C_USER.value)

        db.session.commit()
        return user

    @staticmethod
    def update_user(user_id, data):
        """Updates a user's information."""
        user = User.query.get(user_id)
        if not user:
            raise NotFoundException("User not found.")
        
        if 'email' in data and data['email'] != user.email:
            if User.query.filter_by(email=data['email']).first():
                raise ValidationException("Email address already in use.")
            user.email = data['email']
            
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        
        if 'password' in data and data['password']:
            if not UserService.is_password_strong(data['password']):
                raise ValidationException("New password is not strong enough.")
            user.set_password(data['password'])
            
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_id(user_id):
        user = User.query.get(user_id)
        if not user:
            raise NotFoundException("User not found.")
        return user

    @staticmethod
    def get_all_users(page, per_page):
        """Returns a paginated list of all users."""
        return User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def is_admin(user_id):
        """Checks if a user has the ADMIN role."""
        user = User.query.get(user_id)
        return user and any(role.name == RoleType.ADMIN for role in user.roles)

    @staticmethod
    def is_b2b_user(user_id):
        """Checks if a user has the B2B_USER role."""
        user = User.query.get(user_id)
        return user and any(role.name == RoleType.B2B_USER for role in user.roles)
        
    @staticmethod
    def get_b2b_profile_by_user_id(user_id):
        """Retrieves the B2B profile associated with a user ID."""
        profile = B2BUser.query.filter_by(user_id=user_id).first()
        if not profile:
            raise NotFoundException("B2B profile not found for this user.")
        return profile