from decimal import Decimal
from backend.models import db, User, Role, UserRole, Tier, Order, Company, B2BAccount
from backend.services.email_service import EmailService
from backend.services.user_service import UserService
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from backend.extensions import db
from backend.services.auth_service import AuthService
from backend.services.exceptions import ValidationException, NotFoundException, ServiceError
from flask_login import current_user
from backend.utils.encryption import hash_password
from backend.models.enums import RoleType
from backend.services.audit_log_service import AuditLogService

class B2BService:
    """
    Service layer for managing B2B accounts and related operations.
    """
    def __init__(self):
        self.email_service = EmailService()
        self.user_service = UserService()
        self.auth_service = AuthService()
        self.audit_log_service = AuditLogService()

    def create_b2b_account(self, data):
        """
        Creates a B2B account application.
        This involves creating a User and a linked B2BAccount with 'pending' status.
        """
        if User.query.filter_by(email=data['email']).first():
            raise ValidationException("A user with this email already exists.")

        try:
            # First, create the user record
            user = self.user_service.create_user({
                'email': data['email'],
                'password': data['password'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'is_b2b': True,
                'is_active': False # Account is not active until approved
            })

            # Then, create the B2B account record
            b2b_account = B2BAccount(
                user_id=user.id,
                company_name=data['company_name'],
                vat_number=data.get('vat_number'),
                status='pending'
            )
            db.session.add(b2b_account)
            db.session.commit()

            # Send notifications
            self.email_service.send_b2b_pending_email(user.email, user.first_name)
            # self.email_service.send_admin_b2b_review_email(b2b_account) # Optional: notify admin

            self.audit_log_service.add_entry(
                f"B2B account application submitted for '{b2b_account.company_name}' by '{user.email}'",
                user_id=user.id,
                target_type='b2b_account',
                target_id=b2b_account.id,
                action='create'
            )
            return b2b_account
        except (SQLAlchemyError, Exception) as e:
            db.session.rollback()
            raise ValidationException(f"Error creating B2B account: {e}")

    def approve_b2b_account(self, b2b_account_id):
        """
        Approves a pending B2B account.
        This activates the user, changes the B2B status, and assigns the B2B role.
        """
        b2b_account = B2BAccount.query.get(b2b_account_id)
        if not b2b_account:
            raise NotFoundException("B2B account not found.")
        if b2b_account.status == 'approved':
            raise ServiceError("B2B account is already approved.")

        try:
            # Update status and activate user
            b2b_account.status = 'approved'
            b2b_account.user.is_active = True

            # Assign 'b2b' role
            self.auth_service.add_role_to_user(b2b_account.user, 'b2b')
            
            db.session.commit()

            # Send approval email
            self.email_service.send_b2b_approved_email(b2b_account.user.email, b2b_account.user.first_name)
            
            self.audit_log_service.add_entry(
                f"B2B account approved for '{b2b_account.company_name}'",
                user_id=current_user.id, # The admin performing the action
                target_type='b2b_account',
                target_id=b2b_account.id,
                action='approve'
            )
            return b2b_account
        except (SQLAlchemyError, Exception) as e:
            db.session.rollback()
            raise ServiceError(f"Error approving B2B account: {e}")

    def get_all_b2b_accounts(self, status=None):
        """
        Retrieves all B2B accounts, optionally filtering by status.
        """
        query = B2BAccount.query
        if status:
            query = query.filter(B2BAccount.status == status)
        return query.all()

    def get_b2b_account_by_user_id(self, user_id):
        """Retrieves a B2B account by the associated user ID."""
        b2b_account = B2BAccount.query.filter_by(user_id=user_id).first()
        if not b2b_account:
            raise NotFoundException("B2B account not found for this user.")
        return b2b_account

    def update_b2b_account(self, user_id, data):
        """
        Updates a B2B account and its associated user details.
        """
        b2b_account = self.get_b2b_account_by_user_id(user_id)
        try:
            if 'company_name' in data and data['company_name'] is not None:
                b2b_account.company_name = data['company_name']
            if 'vat_number' in data and data['vat_number'] is not None:
                b2b_account.vat_number = data['vat_number']
            if 'user_details' in data and data['user_details'] is not None:
                self.user_service.update_user(user_id, data['user_details'])
            db.session.commit()
            return b2b_account
        except Exception as e:
            db.session.rollback()
            raise ServiceError(f"Could not update B2B account: {e}")

    def request_b2b_account_deletion(self, user_id):
        """
        Allows a B2B user to soft-delete their own account.
        """
        b2b_account = self.get_b2b_account_by_user_id(user_id)
        try:
            b2b_account.soft_delete()
            b2b_account.user.soft_delete()
            db.session.commit()
            self.audit_log_service.add_entry(
                f"B2B User requested account deletion for '{b2b_account.company_name}'",
                user_id=user_id,
                target_type='b2b_account',
                target_id=b2b_account.id,
                action='soft_delete'
            )
        except Exception as e:
            db.session.rollback()
            raise ServiceError(f"Could not process B2B account deletion: {e}")


    # --- Tier Management Logic ---

    def create_tier(self, name: str, discount_percentage: Decimal, minimum_spend: Decimal = None) -> Tier:
        """Creates a new B2B pricing tier."""
        try:
            new_tier = Tier(
                name=name,
                discount_percentage=Decimal(discount_percentage),
                minimum_spend=Decimal(minimum_spend) if minimum_spend else None
            )
            db.session.add(new_tier)
            db.session.commit()
            self.logger.info(f"Created new B2B tier: {name}")
            return new_tier
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"Error creating tier '{name}': {e}")
            raise

    def get_all_tiers(self) -> list[Tier]:
        """Retrieves all tiers."""
        return db.session.query(Tier).order_by(Tier.minimum_spend.asc()).all()

    def assign_tier_to_user(self, user_id: int, tier_id: int) -> User:
        """Manually assigns a pricing tier to a B2B user."""
        user = self.user_service.get_user_by_id(user_id)
        tier = db.session.query(Tier).get(tier_id)
        if not user or not user.is_b2b:
            raise ValueError("User is not a B2B account.")
        if not tier:
            raise ValueError("Tier not found.")
        
        user.tier_id = tier_id
        db.session.commit()
        self.logger.info(f"Assigned tier '{tier.name}' to user {user.email}.")
        return user

    def update_user_tier_based_on_spend(self, user_id: int) -> User:
        """
        Automatically evaluates and updates a B2B user's tier based on their
        total spending. This should be run periodically or after each order.
        """
        user = self.user_service.get_user_by_id(user_id)
        if not user or not user.is_b2b:
            return None

        total_spend = db.session.query(func.sum(Order.total_price)).filter(Order.user_id == user_id).scalar() or Decimal('0.00')

        # Find the highest applicable tier the user qualifies for
        applicable_tier = db.session.query(Tier)\
            .filter(Tier.minimum_spend <= total_spend)\
            .order_by(Tier.minimum_spend.desc())\
            .first()

        if applicable_tier and user.tier_id != applicable_tier.id:
            self.logger.info(f"User {user.email} (spend: {total_spend}) qualifies for new tier '{applicable_tier.name}'. Updating.")
            user.tier_id = applicable_tier.id
            db.session.commit()
        
        return user
