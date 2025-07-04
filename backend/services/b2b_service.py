from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from backend.database import db
from backend.models import B2BAccount, Tier, User
from backend.services.exceptions import ServiceError, ServiceException


class B2BService:
    """
    Service layer for managing B2B accounts and related operations.
    """

    def __init__(self, session=None):
        self.session = session or db.session
        self.email_service = EmailService()
        self.user_service = UserService()
        self.audit_log_service = AuditLogService()

    def create_b2b_account_and_user(self, company_data, user_data):
        """
        Creates a new B2B account, a company, and the initial admin user for that account.
        This is an atomic transaction.
        """
        # ** FIX: Import AuthService inside the method to break the circular dependency **
        from backend.services.auth_service import AuthService

        auth_service = AuthService(self.session)

        try:
            # Check if company or user email already exists
            if Company.query.filter_by(name=company_data.get("name")).first():
                raise DataConflictException("A company with this name already exists.")
            if User.query.filter_by(email=user_data.get("email")).first():
                raise DataConflictException("A user with this email already exists.")

            # 1. Create the Company
            new_company = Company(name=company_data.get("name"))
            self.session.add(new_company)

            # 2. Create the B2B Account linked to the Company
            new_b2b_account = B2BAccount(company=new_company)
            self.session.add(new_b2b_account)

            # 3. Create the User via the AuthService to handle hashing and roles
            # We need to flush to get the b2b_account.id before creating the user
            self.session.flush()
            user_data["b2b_account_id"] = new_b2b_account.id
            # Ensure the user is created with an 'admin' or 'b2b_admin' role
            new_user = auth_service.create_user(user_data, role_name="b2b_admin")

            self.session.commit()
            return new_b2b_account, new_user

        except Exception as e:
            self.session.rollback()
            # Log the error e
            current_app.logger.error(f"Failed to create B2B account: {e}")
            raise ServiceException(f"Failed to create B2B account: {e}")

    def add_user_to_b2b_account(self, b2b_account_id, user_data, role_name="b2b_user"):
        """
        Adds a new user to an existing B2B account.
        """
        from backend.services.auth_service import AuthService

        auth_service = AuthService(self.session)

        b2b_account = self.session.query(B2BAccount).get(b2b_account_id)
        if not b2b_account:
            raise NotFoundException(
                resource_name="B2B Account", resource_id=b2b_account_id
            )

        user_data["b2b_account_id"] = b2b_account.id
        new_user = auth_service.create_user(user_data, role_name=role_name)

        return new_user

    def approve_b2b_account(self, b2b_account_id):
        """
        Approves a pending B2B account.
        This activates the user, changes the B2B status, and assigns the B2B role.
        """
        b2b_account = B2BAccount.query.get(b2b_account_id)
        if not b2b_account:
            raise NotFoundException("B2B account not found.") from e
        if b2b_account.status == "approved":
            raise ServiceError("B2B account is already approved.") from e

        try:
            # Update status and activate user
            b2b_account.status = "approved"
            if b2b_account.user:
                b2b_account.user.is_active = True

                # Assign 'b2b' role
                from backend.services.auth_service import AuthService

                auth_service = AuthService(self.session)
                auth_service.add_role_to_user(b2b_account.user, "b2b")

            db.session.commit()

            # Send approval email
            if b2b_account.user:
                self.email_service.send_b2b_approved_email(
                    b2b_account.user.email, b2b_account.user.first_name
                )

            self.audit_log_service.add_entry(
                f"B2B account approved for '{b2b_account.company.name}'",
                user_id=current_user.id,  # The admin performing the action
                target_type="b2b_account",
                target_id=b2b_account.id,
                action="approve",
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
        user = User.query.get(user_id)
        if not user or not user.b2b_account:
            raise NotFoundException("B2B account not found for this user.") from e
        return user.b2b_account

    def update_b2b_account(self, b2b_account_id, data):
        """
        Updates a B2B account and its associated company details.
        """
        b2b_account = B2BAccount.query.get(b2b_account_id)
        if not b2b_account:
            raise NotFoundException("B2B Account not found.") from e
        try:
            if "company_name" in data and data["company_name"] is not None:
                b2b_account.company.name = data["company_name"]
            if "vat_number" in data and data["vat_number"] is not None:
                b2b_account.vat_number = data["vat_number"]
            # User details should be updated via UserService
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
            for user in b2b_account.users:
                user.soft_delete()
            db.session.commit()
            self.audit_log_service.add_entry(
                f"B2B User requested account deletion for '{b2b_account.company.name}'",
                user_id=user_id,
                target_type="b2b_account",
                target_id=b2b_account.id,
                action="soft_delete",
            )
        except Exception as e:
            db.session.rollback()
            raise ServiceError(f"Could not process B2B account deletion: {e}")

    # --- Tier Management Logic ---

    def create_tier(
        self, name: str, discount_percentage: Decimal, minimum_spend: Decimal = None
    ) -> Tier:
        """Creates a new B2B pricing tier."""
        try:
            new_tier = Tier(
                name=name,
                discount_percentage=Decimal(discount_percentage),
                minimum_spend=Decimal(minimum_spend) if minimum_spend else None,
            )
            db.session.add(new_tier)
            db.session.commit()
            current_app.logger.info(f"Created new B2B tier: {name}")
            return new_tier
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating tier '{name}': {e}")
            raise

    def get_all_tiers(self) -> list[Tier]:
        """Retrieves all tiers."""
        return db.session.query(Tier).order_by(Tier.minimum_spend.asc()).all()

    def assign_tier_to_user(self, user_id: int, tier_id: int) -> User:
        """Manually assigns a pricing tier to a B2B user."""
        user = self.user_service.get_user_by_id(user_id)
        tier = db.session.query(Tier).get(tier_id)
        if not user or not user.b2b_account:
            raise ValueError("User is not a B2B account.") from e
        if not tier:
            raise ValueError("Tier not found.") from e

        user.tier_id = tier_id
        db.session.commit()
        current_app.logger.info(f"Assigned tier '{tier.name}' to user {user.email}.")
        return user

    def update_user_tier_based_on_spend(self, user_id: int) -> User:
        """
        Automatically evaluates and updates a B2B user's tier based on their
        total spending. This should be run periodically or after each order.
        """
        user = self.user_service.get_user_by_id(user_id)
        if not user or not user.b2b_account:
            return None

        total_spend = db.session.query(func.sum(Order.total_price)).filter(
            Order.user_id == user_id
        ).scalar() or Decimal("0.00")

        # Find the highest applicable tier the user qualifies for
        applicable_tier = (
            db.session.query(Tier)
            .filter(Tier.minimum_spend <= total_spend)
            .order_by(Tier.minimum_spend.desc())
            .first()
        )

        if applicable_tier and user.tier_id != applicable_tier.id:
            current_app.logger.info(
                f"User {user.email} (spend: {total_spend}) qualifies for new tier '{applicable_tier.name}'. Updating."
            )
            user.tier_id = applicable_tier.id
            db.session.commit()

        return user
