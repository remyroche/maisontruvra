from backend.database import db
from backend.services.monitoring_service import MonitoringService
from backend.services.exceptions import NotFoundException, ValidationException, UnauthorizedException
from backend.utils.input_sanitizer import InputSanitizer
from backend.services.audit_log_service import AuditLogService
from flask import current_app, request, g
from flask_jwt_extended import get_jwt_identity
from backend.models import User, Address, UserRole
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from backend.extensions import db


class UserService:

    def __init__(self, logger):
        self.logger = logger

    def get_user_by_id(self, user_id):
        """Retrieves a user by their ID."""
        try:
            return db.session.query(User).get(user_id)
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving user by ID {user_id}: {e}")
            raise

    def get_user_by_email(self, email):
        """Retrieves a user by their email address."""
        try:
            return db.session.query(User).filter_by(email=email).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving user by email {email}: {e}")
            raise

    def get_or_create_guest_user(self, email, first_name, last_name):
        """
        Retrieves an existing user or creates a new, inactive guest user.
        This is for guest checkout.
        """
        try:
            user = self.get_user_by_email(email)
            if user:
                # If user exists but is a guest, we can reuse it.
                # If they are a registered user, we should prompt them to log in.
                if not user.is_guest:
                    raise ValueError("An account with this email already exists. Please log in.")
                return user

            # Create a new guest user
            guest_user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=False, # Remains inactive
                is_guest=True
            )
            db.session.add(guest_user)
            db.session.commit()
            self.logger.info(f"Created new guest user account for {email}.")
            return guest_user
        except (SQLAlchemyError, IntegrityError, ValueError) as e:
            db.session.rollback()
            self.logger.error(f"Error creating guest user for {email}: {e}")
            raise

    def update_user_profile(self, user_id, profile_data):
        """Updates a user's profile information."""
        try:
            user = self.get_user_by_id(user_id)
            if user:
                user.email = profile_data.get('email', user.email)
                user.first_name = profile_data.get('first_name', user.first_name)
                user.last_name = profile_data.get('last_name', user.last_name)
                db.session.commit()
                self.logger.info(f"User profile for {user_id} updated.")
                return user
            return None
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"Error updating profile for user {user_id}: {e}")
            raise

    def get_user_addresses(self, user_id):
        """Retrieves all addresses for a given user."""
        try:
            return db.session.query(Address).filter_by(user_id=user_id).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving addresses for user {user_id}: {e}")
            raise
    
    def get_all_users(self, page=1, per_page=20):
        """Retrieves all users with pagination for admin purposes."""
        try:
            return User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving all users: {e}")
            raise


    @staticmethod
    def get_user_profile(self, user_id):
        user = User.query.get_or_404(user_id)
        return user.to_dict()

    @staticmethod
    def update_profile(self, user_id, data):
        """ Updates a user's profile after sanitizing inputs. """
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")

        if 'first_name' in data:
            user.first_name = InputSanitizer.sanitize_input(data['first_name'])
        if 'last_name' in data:
            user.last_name = InputSanitizer.sanitize_input(data['last_name'])
        if 'email' in data:
            new_email = data['email'].lower()
            if new_email != user.email:
                if User.query.filter_by(email=new_email).first():
                    raise ValueError("Email already in use.")
                user.email = new_email

        db.session.commit()
        current_app.logger.info(f"User profile updated for {user.email}")
        return user

    @staticmethod
    def admin_update_user(self, user_id, data):
        """ Allows an admin to update user details. """
        user = User.query.get(user_id)
        if not user:
            return None

        # Use the regular profile update logic for common fields
        self.update_profile(user_id, data)

        # Admin-specific fields
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'roles' in data:
            # This requires logic to fetch Role objects from the DB
            # and assign them to the user.roles relationship.
            # Example: user.roles = Role.query.filter(Role.name.in_(data['roles'])).all()
            pass

        db.session.commit()
        current_app.logger.info(f"Admin updated profile for {user.email}")
        return user

    @staticmethod
    def admin_create_user(self, data):
        """ Allows an admin to create a new user. """
        from backend.services.auth_service import AuthService
        # Reusing the registration logic is better to keep things DRY
        auth_service = AuthService()
        user = auth_service.register_user(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=data['password']
        )
        
        # Admins might set additional properties upon creation
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        db.session.commit()
        current_app.logger.info(f"Admin created new user: {user.email}")
        return user
        
        


    @staticmethod
    def create_user(user_data: dict):
        """Create a new user with proper validation and logging."""
        user_data = InputSanitizer.sanitize_input(user_data)

        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not user_data.get(field):
                raise ValidationException(f"Field '{field}' is required")

        # Check if user already exists
        if User.query.filter_by(email=user_data['email']).first():
            raise ValidationException("User with this email already exists")

        browser_lang = request.accept_languages.best_match(['en', 'fr'], default='en')

        try:
            user = User(
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data.get('role', UserRole.B2C),
                is_active=user_data.get('is_active', True),
                language=browser_lang
            )
            user.set_password(user_data['password'])

            db.session.add(user)
            db.session.flush()  # Get ID before commit

            # Log the action
            AuditLogService.log_action(
                'USER_CREATED',
                target_id=user.id,
                details={'email': user.email, 'role': user.role.value}
            )

            db.session.commit()

            MonitoringService.log_info(f"User created successfully: {user.email} (ID: {user.id})", "UserService")
            return user.to_dict(context='admin')

        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(f"Failed to create user: {str(e)}", "UserService")
            raise ValidationException(f"Failed to create user: {str(e)}")

    def update_user_language(self, user_id, language, user_type='b2c'):
        if user_type == 'b2c':
            user = self.db.session.get(User, user_id)
        else:
            user = self.db.session.get(B2BUser, user_id)
            
        if not user:
            raise ValueError("User not found")
        if language not in ['en', 'fr']:
            raise ValueError("Unsupported language")
            
        user.language = language
        self.db.session.commit()
        return user
    

    @staticmethod
    def delete_user(user_id: int):
        """Soft delete user with logging."""
        user = User.query.get(user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")

        try:
            user.is_active = False
            user.deleted_at = db.func.now()

            db.session.flush()

            AuditLogService.log_action(
                'USER_DELETED',
                target_id=user.id,
                details={'email': user.email}
            )

            db.session.commit()

            MonitoringService.log_error(f"Failed to update user {user_id}: {str(e)}", "UserService")

        except Exception as e:
            db.session.rollback()
            MonitoringService.log_info(f"User created successfully: {user.email} (ID: {user.id})", "UserService")
            raise ValidationException(f"Failed to delete user: {str(e)}")


# Standalone functions for backward compatibility
def get_user_by_id(user_id):
    """Standalone function to get user by ID"""
    service = UserService()
    return service.get_user_by_id(user_id)
