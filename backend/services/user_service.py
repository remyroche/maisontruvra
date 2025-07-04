from flask import current_app
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.extensions import db
from backend.models import Address, AdminAuditLog, Company, Role, User
from backend.models.enums import RoleType
from backend.services.audit_log_service import AuditLogService
from backend.services.exceptions import (
    DeletionException,
    NotFoundException,
    UpdateException,
    UserNotFoundException,
    ValidationException,
)
from backend.services.monitoring_service import MonitoringService
from backend.utils.input_sanitizer import InputSanitizer

audit_log_service = AuditLogService()


class UserService:
    def __init__(self, logger):
        self.logger = logger
        self.session = db.session
        self.audit_log_service = AuditLogService()
        self.monitoring_service = MonitoringService()

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
                    raise ValueError(
                        "An account with this email already exists. Please log in."
                    )
                return user

            # Create a new guest user
            guest_user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=False,  # Remains inactive
                is_guest=True,
            )
            db.session.add(guest_user)
            db.session.commit()
            self.logger.info(f"Created new guest user account for {email}.")
            return guest_user
        except (SQLAlchemyError, IntegrityError, ValueError) as e:
            db.session.rollback()
            self.logger.error(f"Error creating guest user for {email}: {e}")
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
            return User.query.order_by(User.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving all users: {e}")
            raise

    def get_user_profile(self, user_id):
        user = User.query.get_or_404(user_id)
        return user.to_dict()

    def update_profile(self, user_id, data):
        """Updates a user's profile after sanitizing inputs."""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")

        if "first_name" in data:
            user.first_name = InputSanitizer.sanitize_input(data["first_name"])
        if "last_name" in data:
            user.last_name = InputSanitizer.sanitize_input(data["last_name"])
        if "email" in data:
            new_email = data["email"].lower()
            if new_email != user.email:
                if User.query.filter_by(email=new_email).first():
                    raise ValueError("Email already in use.")
                user.email = new_email

        db.session.commit()
        current_app.logger.info(f"User profile updated for {user.email}")
        return user

    def admin_update_user(self, user_id, data):
        """Allows an admin to update user details."""
        user = User.query.get(user_id)
        if not user:
            return None

        # Use the regular profile update logic for common fields
        self.update_profile(user_id, data)

        # Admin-specific fields
        if "is_active" in data:
            user.is_active = data["is_active"]
        if "roles" in data:
            # This requires logic to fetch Role objects from the DB
            # and assign them to the user.roles relationship.
            # Example: user.roles = Role.query.filter(Role.name.in_(data['roles'])).all()
            pass

        db.session.commit()
        current_app.logger.info(f"Admin updated profile for {user.email}")
        return user

    def admin_create_user(self, data):
        """Allows an admin to create a new user."""
        from backend.services.auth_service import AuthService

        # Reusing the registration logic is better to keep things DRY
        auth_service = AuthService(self.logger)  # Pass logger
        user = auth_service.register_user(data)

        # Admins might set additional properties upon creation
        if "is_active" in data:
            user.is_active = data["is_active"]

        b2c_role = db.session.query(Role).filter_by(name=RoleType.B2C_USER).first()
        if b2c_role:
            user.roles.append(b2c_role)

        db.session.commit()
        current_app.logger.info(f"Admin created new user: {user.email}")
        return user

    def _create_user_logic(
        self, user_data: dict, role: Role, user_type: str, company_id: int = None
    ):
        """
        Méthode privée et centralisée pour créer un utilisateur avec validation,
        nettoyage des données et journalisation robustes.
        """
        sanitized_data = InputSanitizer.sanitize_input(user_data)

        # Valider les champs requis
        required_fields = ["email", "password", "first_name", "last_name"]
        for field in required_fields:
            if not sanitized_data.get(field):
                raise ValidationException(f"Le champ '{field}' est requis.")

        # Vérifier si l'utilisateur existe déjà
        if self.get_user_by_email(sanitized_data["email"]):
            raise ValidationException("Un utilisateur avec cet e-mail existe déjà.")

        # NOTE : L'exemple fourni détecte la langue du navigateur.
        # Pour l'activer, ajoutez une colonne 'language' au modèle User.
        # browser_lang = request.accept_languages.best_match(['en', 'fr'], default='en')

        try:
            new_user = User(
                email=sanitized_data["email"],
                first_name=sanitized_data["first_name"],
                last_name=sanitized_data["last_name"],
                user_type=user_type,
                company_id=company_id,
                # language=browser_lang # Décommentez après avoir ajouté la colonne au modèle User
            )
            new_user.set_password(sanitized_data["password"])
            new_user.roles.append(role)

            self.session.add(new_user)
            self.session.flush()  # Obtenir l'ID de l'utilisateur avant le commit pour la journalisation

            # Journaliser l'action de création
            role_name = role.name.value if hasattr(role.name, "value") else role.name
            self.audit_log_service.log_action(
                action="USER_CREATED",
                target_id=new_user.id,
                details={
                    "email": new_user.email,
                    "role": role_name,
                    "user_type": user_type,
                },
            )

            self.session.commit()

            self.monitoring_service.log_info(
                f"Utilisateur créé avec succès: {new_user.email} (ID: {new_user.id})",
                "UserService",
            )
            return new_user

        except Exception as e:
            self.session.rollback()
            self.monitoring_service.log_error(
                f"Échec de la création de l'utilisateur: {str(e)}", "UserService"
            )
            # Propagez une exception plus conviviale à l'appelant
            raise ValidationException(
                "Une erreur technique est survenue lors de la création de l'utilisateur."
            )

    def create_b2c_user(self, user_data: dict):
        """Crée un nouvel utilisateur B2C avec validation et journalisation complètes."""
        b2c_role = self.session.query(Role).filter_by(name=RoleType.B2C_USER).first()
        if not b2c_role:
            self.monitoring_service.log_error(
                "Le rôle B2C n'a pas été trouvé dans la base de données.", "UserService"
            )
            raise Exception("La configuration du système de rôles est incomplète.")

        return self._create_user_logic(user_data, b2c_role, "b2c_user")

    def create_b2b_user(self, user_data: dict, company_id: int):
        """Crée un nouvel utilisateur B2B avec validation et journalisation complètes."""
        company = self.session.get(Company, company_id)
        if not company:
            raise ValidationException("Entreprise non trouvée.")

        b2b_role = self.session.query(Role).filter_by(name=RoleType.B2B_USER).first()
        if not b2b_role:
            self.monitoring_service.log_error(
                "Le rôle B2B n'a pas été trouvé dans la base de données.", "UserService"
            )
            raise Exception("La configuration du système de rôles est incomplète.")

        return self._create_user_logic(
            user_data, b2b_role, "b2b_user", company_id=company.id
        )

    def update_user_language(self, user_id, language, user_type="b2c"):
        if user_type == "b2c":
            user = db.session.get(User, user_id)
        else:
            user = db.session.get(User, user_id)

        if not user:
            raise ValueError("User not found")
        if language not in ["en", "fr"]:
            raise ValueError("Unsupported language")

        user.language = language
        db.session.commit()
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
                "USER_DELETED", target_id=user.id, details={"email": user.email}
            )

            db.session.commit()

            MonitoringService.log_info(
                f"User soft deleted successfully: {user.email} (ID: {user.id})",
                "UserService",
            )

        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(
                f"Failed to delete user {user_id}: {str(e)}", "UserService"
            )
            raise ValidationException(f"Failed to delete user: {str(e)}")

    def get_user_by_id(self, user_id):
        """Retrieves a user by their ID."""
        user = User.query.get(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} not found.")
        return user

    def update_user(self, user_id, data):
        """Updates a user's information."""
        user = self.get_user_by_id(user_id)
        try:
            for key, value in data.items():
                if key == "password":
                    user.set_password(value)
                elif hasattr(user, key):
                    setattr(user, key, value)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise UpdateException(f"Could not update user: {e}")

    def deactivate_user(self, user_id):
        """
        Admin action to deactivate a user account.
        This is a hard delete, intended for admin use.
        """
        user = self.get_user_by_id(user_id)
        try:
            db.session.delete(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise DeletionException(f"Could not deactivate user: {e}")

    def request_account_deletion(self, user_id):
        """
        Allows a user to soft-delete their own account.
        Logs out the user after deletion.
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} not found.")

        try:
            user.soft_delete()
            db.session.commit()
            # The audit log service will use current_user if available
            audit_log_service.add_entry(
                f"User requested account deletion for '{user.email}'",
                user_id=user.id,
                target_type="user",
                target_id=user.id,
                action="soft_delete",
            )
        except Exception as e:
            db.session.rollback()
            raise DeletionException(f"Could not process account deletion: {e}")

    def get_user_activity(self, user_id):
        """Retrieves user activity logs."""
        self.get_user_by_id(user_id)  # Ensures user exists
        logs = AdminAuditLog.query.filter_by(user_id=user_id).all()
        return [log.to_dict() for log in logs]
