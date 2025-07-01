from backend.database import db
from backend.models.user_models import User, UserRole
from backend.services.monitoring_service import MonitoringService
from backend.services.exceptions import NotFoundException, ValidationException, UnauthorizedException
from backend.utils.input_sanitizer import InputSanitizer
from backend.services.audit_log_service import AuditLogService
from flask import current_app, request, g  # Ensure request is imported
from flask_jwt_extended import get_jwt_identity
from backend.models.b2b_models import B2BUser  # Add this import
from backend.services.audit_log_service import AuditLogService
from backend.utils.input_sanitizer import sanitize_input


class UserService:

    def __init__(self, audit_log_service: AuditLogService):
        self.audit_log_service = audit_log_service


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
            user.first_name = sanitize_input(data['first_name'])
        if 'last_name' in data:
            user.last_name = sanitize_input(data['last_name'])
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
    def get_user_by_id(user_id: int, context: str = 'basic'):
        user = User.query.get_or_404(user_id)
        return user.to_dict()

        
    @staticmethod
    def get_all_users_paginated(page: int, per_page: int, filters: dict = None):
        """Get paginated users with N+1 optimization."""
        query = User.query

        if filters:
            filters = InputSanitizer.sanitize_input(filters)
            if filters.get('role'):
                query = query.filter(User.role == filters['role'])
            if filters.get('is_active') is not None:
                query = query.filter(User.is_active == filters['is_active'])
            if filters.get('email'):
                query = query.filter(User.email.ilike(f"%{filters['email']}%"))

        # Optimize query to avoid N+1 problem
        query = query.options(db.selectinload(User.addresses))

        return query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

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
            user = self.session.get(User, user_id)
        else:
            user = self.session.get(B2BUser, user_id)
            
        if not user:
            raise ValueError("User not found")
        if language not in ['en', 'fr']:
            raise ValueError("Unsupported language")
            
        user.language = language
        self.session.commit()
        return user
    
    @staticmethod
    def update_user(user_id: int, update_data: dict):
        """Update user with proper validation and logging."""
        update_data = InputSanitizer.sanitize_input(update_data)

        user = User.query.get(user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")

        try:
            original_data = {
                'email': user.email,
                'role': user.role.value,
                'is_active': user.is_active
            }

            # Update fields
            if 'email' in update_data and update_data['email'] != user.email:
                # Check email uniqueness
                existing = User.query.filter_by(email=update_data['email']).first()
                if existing and existing.id != user_id:
                    raise ValidationException("Email already in use")
                user.email = update_data['email']

            if 'first_name' in update_data:
                user.first_name = update_data['first_name']
            if 'last_name' in update_data:
                user.last_name = update_data['last_name']
            if 'role' in update_data:
                user.role = UserRole(update_data['role'])
            if 'is_active' in update_data:
                user.is_active = update_data['is_active']

            db.session.flush()

            # Log the action with changes
            changes = {}
            for key, original_value in original_data.items():
                current_value = getattr(user, key)
                if hasattr(current_value, 'value'):
                    current_value = current_value.value
                if original_value != current_value:
                    changes[key] = {'from': original_value, 'to': current_value}

            db.session.commit()

            # Log the update action
            actor_id = g.user.id if g.user else 'system'
            UserService.audit_log_service.log_admin_action(
                user_id=actor_id,
                action=f"Updated user profile",
                target_id=user.id,
                target_type="User",
                details=update_data 
            )

            MonitoringService.log_info(f"User created successfully: {user.email} (ID: {user.id})", "UserService")
            return user.to_dict(context='admin')

        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(f"Failed to update user {user_id}: {str(e)}", "UserService")
            raise ValidationException(f"Failed to update user: {str(e)}")

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
