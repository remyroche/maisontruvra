from backend.models.user_models import User
from backend.models.order_models import Order
from backend.database import db
from backend.services.exceptions import NotFoundException, ServiceException
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

class UserService:
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        user = User.query.get(user_id)
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")
        return user

    @staticmethod
    def get_user_by_email(email):
        """Get user by email"""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def create_user(data):
        """Create new user"""
        existing_user = UserService.get_user_by_email(data.get('email'))
        if existing_user:
            raise ServiceException("User with this email already exists")

        try:
            user_data = data.copy()
            if 'password' in user_data:
                user_data['password_hash'] = generate_password_hash(user_data.pop('password'))

            user = User(**user_data)
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise ServiceException(f"Failed to create user: {str(e)}")

    @staticmethod
    def update_user(user_id, data):
        """Update user"""
        user = UserService.get_user_by_id(user_id)
        try:
            for key, value in data.items():
                if key == 'password':
                    user.password_hash = generate_password_hash(value)
                elif hasattr(user, key):
                    setattr(user, key, value)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise ServiceException(f"Failed to update user: {str(e)}")

    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user"""
        user = UserService.get_user_by_email(email)
        if user and check_password_hash(user.password_hash, password):
            return user
        return None

    @staticmethod
    def get_user_orders(user_id):
        """Get user's orders"""
        return Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()

    @staticmethod
    def delete_user(user_id):
        """Delete user"""
        user = UserService.get_user_by_id(user_id)
        try:
            db.session.delete(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ServiceException(f"Failed to delete user: {str(e)}")
