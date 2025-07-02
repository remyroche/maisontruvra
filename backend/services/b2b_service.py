from decimal import Decimal
from backend.models import db, User, Role, UserRole, Tier, Order, Company
from backend.services.email_service import EmailService
from backend.services.user_service import UserService
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from backend.extensions import db
from backend.utils.encryption import hash_password
from backend.models.enums import RoleType
from backend.services.audit_log_service import AuditLogService

class B2BService:
    def __init__(self, logger):
        self.logger = logger
        self.email_service = EmailService(logger)
        self.user_service = UserService(logger)
        self.audit_log_service = AuditLogService()

    def create_b2b_account(self, data):
        """
        Creates a B2B user account, which is initially pending approval.
        """
        try:
            if db.session.query(User).filter_by(email=data['email']).first():
                raise ValueError("B2B user with this email already exists.")

            hashed_password = hash_password(data['password'])
            
            b2b_user = User(
                email=data['email'],
                password_hash=hashed_password,
                company_name=data['company_name'],
                contact_person=data['contact_person'],
                status='pending'
            )
            db.session.add(b2b_user)
            db.session.commit()

            # Send email to admin for approval and to user for confirmation
            subject = "Your B2B Account Application is Pending Approval"
            template = "b2b_account_pending"
            context = {"b2b_user": b2b_user}
            self.email_service.send_email(b2b_user.email, subject, template, context)
            
            # TODO: Send notification to admin dashboard

            self.logger.info(f"B2B account created for {data['email']} and is pending approval.")
            return b2b_user
        except (SQLAlchemyError, ValueError) as e:
            db.session.rollback()
            self.logger.error(f"Error creating B2B account: {e}")
            raise

    def approve_b2b_account(self, b2b_user_id):
        """
        Approves a B2B user account and assigns the 'b2b_user' role.
        """
        try:
            b2b_user = db.session.query(User).get(b2b_user_id)
            if not b2b_user:
                raise ValueError("B2B user not found.")

            b2b_user.status = 'approved'
            
            # Assign 'b2b_user' role
            b2b_role = db.session.query(Role).filter_by(name='b2b_user').first()
            if b2b_role:
                # Check if role is already assigned
                existing_role = db.session.query(UserRole).filter_by(user_id=b2b_user.id, role_id=b2b_role.id).first()
                if not existing_role:
                    user_role = UserRole(user_id=b2b_user.id, role_id=b2b_role.id)
                    db.session.add(user_role)
            
            db.session.commit()

            # Send approval email
            subject = "Your B2B Account has been Approved!"
            template = "b2b_account_approved"
            context = {"b2b_user": b2b_user}
            self.email_service.send_email(b2b_user.email, subject, template, context)

            self.logger.info(f"B2B account {b2b_user.email} has been approved.")
            return b2b_user
        except (SQLAlchemyError, ValueError) as e:
            db.session.rollback()
            self.logger.error(f"Error approving B2B account: {e}")
            raise

    def get_b2b_account_by_user_id(self, user_id):
        """Retrieves a B2B account by user ID."""
        b2b_account = B2BAccount.query.filter_by(user_id=user_id).first()
        if not b2b_account:
            raise NotFoundException("B2B account not found for this user.")
        return b2b_account

    def request_b2b_account_deletion(self, user_id):
        """
        Allows a B2B user to soft-delete their own account.
        This will also soft-delete the associated user record.
        """
        b2b_account = self.get_b2b_account_by_user_id(user_id)
        user = self.user_service.get_user_by_id(user_id)

        try:
            b2b_account.soft_delete()
            user.soft_delete() # Also soft-delete the underlying user
            db.session.commit()
            
            self.audit_log_service.add_entry(
                f"B2B User requested account deletion for '{b2b_account.company_name}'",
                user_id=user.id,
                target_type='b2b_account',
                target_id=b2b_account.id,
                action='soft_delete'
            )
        except Exception as e:
            db.session.rollback()
            raise DeletionException(f"Could not process B2B account deletion: {e}")


    def get_all_b2b_users(self):
        """Récupère tous les utilisateurs avec un rôle B2B."""
        return self.session.query(User).join(User.roles).filter(Role.name == RoleType.B2B_USER).all()
        
    def update_b2b_user_profile(self, user_id: int, data: dict):
        """Met à jour le profil d'un utilisateur B2B."""
        user = self.get_b2b_user_by_id(user_id)
        if not user:
            raise ValueError("Utilisateur B2B non trouvé.")
        
        for key, value in data.items():
            if hasattr(user, key) and key != 'password':
                setattr(user, key, value)
        
        self.session.commit()
        return user

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
