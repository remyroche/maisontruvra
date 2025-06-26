from backend.database import db
from backend.models.user_models import User, UserRole
from backend.services.exceptions import NotFoundException, ValidationException, UnauthorizedException
from backend.utils.sanitization import sanitize_input
from backend.services.audit_log_service import AuditLogService
from flask import current_app
from flask_jwt_extended import get_jwt_identity
import logging

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    def get_user_by_id(user_id: int, context: str = 'basic'):
        """Get user by ID with different serialization contexts."""
        user = User.query.get(user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")

        return user.to_dict(context=context)

    @staticmethod
    def get_all_users_paginated(page: int, per_page: int, filters: dict = None):
        """Get paginated users with N+1 optimization."""
        query = User.query

        if filters:
            filters = sanitize_input(filters)
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
        user_data = sanitize_input(user_data)

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
                is_active=user_data.get('is_active', True)
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

            logger.info(f"User created successfully: {user.email} (ID: {user.id})")
            return user.to_dict(context='admin')

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create user: {str(e)}")
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
        update_data = sanitize_input(update_data)

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

            if changes:
                AuditLogService.log_action(
                    'USER_UPDATED',
                    target_id=user.id,
                    details={'changes': changes}
                )

            db.session.commit()

            logger.info(f"User updated successfully: {user.email} (ID: {user.id})")
            return user.to_dict(context='admin')

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update user {user_id}: {str(e)}")
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

            logger.info(f"User soft deleted: {user.email} (ID: {user.id})")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to delete user {user_id}: {str(e)}")
            raise ValidationException(f"Failed to delete user: {str(e)}")
