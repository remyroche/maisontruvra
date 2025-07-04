import secrets
import string
from datetime import datetime

from backend.database import db
from backend.models.referral_models import Referral
from backend.models.user_models import User
from backend.services.audit_log_service import AuditLogService
from backend.services.exceptions import (
    NotFoundException,
    ReferralException,
    ServiceError,
    ValidationException,
)
from backend.services.loyalty_service import LoyaltyService
from backend.services.monitoring_service import MonitoringService
from backend.services.notification_service import NotificationService
from backend.utils.input_sanitizer import InputSanitizer


class ReferralService:
    """Service for managing user referrals and referral rewards"""

    def __init__(self, session=None):
        self.session = session or db.session
        self.loyalty_service = LoyaltyService()
        self.notification_service = NotificationService()

    @staticmethod
    def generate_referral_code(user_id):
        """Generate a unique referral code for a user"""
        try:
            user_id = InputSanitizer.sanitize_input(user_id)

            # Verify user exists
            user = User.query.get(user_id)
            if not user:
                raise NotFoundException("User not found")

            # Check if user already has a referral code
            existing_referral = Referral.query.filter_by(referrer_id=user_id).first()
            if existing_referral and existing_referral.referral_code:
                return existing_referral.referral_code

            # Generate a unique referral code
            while True:
                code = "".join(
                    secrets.choice(string.ascii_uppercase + string.digits)
                    for _ in range(8)
                )
                if not Referral.query.filter_by(referral_code=code).first():
                    break

            # Create or update referral record
            if existing_referral:
                existing_referral.referral_code = code
                referral = existing_referral
            else:
                referral = Referral(
                    referrer_id=user_id,
                    referral_code=code,
                    created_at=datetime.utcnow(),
                )
                db.session.add(referral)

            db.session.commit()

            # Log the action
            AuditLogService.log_action(
                user_id=user_id,
                action="GENERATE_REFERRAL_CODE",
                resource_type="REFERRAL",
                resource_id=referral.id,
                details=f"Generated referral code: {code}",
            )

            MonitoringService.log_info(
                f"Generated referral code {code} for user {user_id}",
                "ReferralService",
            )
            return code

        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(
                f"Error generating referral code for user {user_id}: {str(e)}"
            )
            raise ServiceError(f"Failed to generate referral code: {str(e)}")

    @staticmethod
    def apply_referral_code(user_id, referral_code):
        """Apply a referral code when a user signs up"""
        try:
            user_id = InputSanitizer.sanitize_input(user_id)
            referral_code = InputSanitizer.sanitize_input(referral_code)

            # Verify user exists
            user = User.query.get(user_id)
            if not user:
                raise NotFoundException("User not found")

            # Find the referral record
            referral = Referral.query.filter_by(referral_code=referral_code).first()
            if not referral:
                raise NotFoundException("Invalid referral code")

            # Check if user is trying to refer themselves
            if referral.referrer_id == user_id:
                raise ValidationException("Cannot use your own referral code")

            # Check if user has already been referred
            existing_referral = Referral.query.filter_by(referred_id=user_id).first()
            if existing_referral:
                raise ValidationException("User has already been referred")

            # Apply the referral
            referral.referred_id = user_id
            referral.status = "pending"
            referral.referred_at = datetime.utcnow()

            db.session.commit()

            # Log the action
            AuditLogService.log_action(
                user_id=user_id,
                action="APPLY_REFERRAL_CODE",
                resource_type="REFERRAL",
                resource_id=referral.id,
                details=f"Applied referral code: {referral_code}",
            )

            MonitoringService.log_info(
                f"User {user_id} applied referral code {referral_code}",
                "ReferralService",
            )
            return True

        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(
                f"Error applying referral code {referral_code} for user {user_id}: {str(e)}"
            )
            raise ServiceError(f"Failed to apply referral code: {str(e)}")

    @staticmethod
    def complete_referral(user_id):
        """Complete a referral when the referred user makes their first purchase"""
        try:
            user_id = InputSanitizer.sanitize_input(user_id)

            # Find the referral record for this user
            referral = Referral.query.filter_by(
                referred_id=user_id, status="pending"
            ).first()
            if not referral:
                return False  # No pending referral found

            # Mark referral as completed
            referral.status = "completed"
            referral.completed_at = datetime.utcnow()

            db.session.commit()

            # Log the action
            AuditLogService.log_action(
                user_id=user_id,
                action="COMPLETE_REFERRAL",
                resource_type="REFERRAL",
                resource_id=referral.id,
                details=f"Completed referral for user {user_id}",
            )

            MonitoringService.log_info(
                f"Completed referral for user {user_id}", "ReferralService"
            )
            return True

        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(
                f"Error completing referral for user {user_id}: {str(e)}"
            )
            raise ServiceError(f"Failed to complete referral: {str(e)}")

    @staticmethod
    def get_user_referrals(user_id):
        """Get all referrals made by a user"""
        try:
            user_id = InputSanitizer.sanitize_input(user_id)

            # Verify user exists
            user = User.query.get(user_id)
            if not user:
                raise NotFoundException("User not found")

            referrals = Referral.query.filter_by(referrer_id=user_id).all()

            result = []
            for referral in referrals:
                referred_user = (
                    User.query.get(referral.referred_id)
                    if referral.referred_id
                    else None
                )
                result.append(
                    {
                        "id": referral.id,
                        "referral_code": referral.referral_code,
                        "referred_user": {
                            "id": referred_user.id,
                            "email": referred_user.email,
                        }
                        if referred_user
                        else None,
                        "status": referral.status,
                        "created_at": referral.created_at.isoformat()
                        if referral.created_at
                        else None,
                        "referred_at": referral.referred_at.isoformat()
                        if referral.referred_at
                        else None,
                        "completed_at": referral.completed_at.isoformat()
                        if referral.completed_at
                        else None,
                    }
                )

            return result

        except Exception as e:
            MonitoringService.log_error(
                f"Error getting referrals for user {user_id}: {str(e)}"
            )
            raise ServiceError(f"Failed to get referrals: {str(e)}")

    @staticmethod
    def get_referral_stats(user_id):
        """Get referral statistics for a user"""
        try:
            user_id = InputSanitizer.sanitize_input(user_id)

            # Verify user exists
            user = User.query.get(user_id)
            if not user:
                raise NotFoundException("User not found")

            total_referrals = (
                Referral.query.filter_by(referrer_id=user_id)
                .filter(Referral.referred_id.isnot(None))
                .count()
            )
            completed_referrals = Referral.query.filter_by(
                referrer_id=user_id, status="completed"
            ).count()
            pending_referrals = Referral.query.filter_by(
                referrer_id=user_id, status="pending"
            ).count()

            # Get user's referral code
            referral_record = Referral.query.filter_by(referrer_id=user_id).first()
            referral_code = referral_record.referral_code if referral_record else None

            return {
                "referral_code": referral_code,
                "total_referrals": total_referrals,
                "completed_referrals": completed_referrals,
                "pending_referrals": pending_referrals,
            }

        except Exception as e:
            MonitoringService.log_error(
                f"Error getting referral stats for user {user_id}: {str(e)}"
            )
            raise ServiceError(f"Failed to get referral stats: {str(e)}")

    def process_referral(self, new_user_id, referral_code):
        """
        Processes a referral code for a new user.
        - Validates the code
        - Awards points/credit to referrer and new user
        - Sends notifications
        """
        # Find the user who owns the referral code.
        referrer = User.query.filter_by(referral_code=referral_code).first()
        if not referrer:
            raise ReferralException("Invalid referral code.")

        new_user = User.query.get(new_user_id)
        if not new_user:
            raise ReferralException("New user not found.")

        if new_user.id == referrer.id:
            raise ReferralException("Cannot refer yourself.")

        # Check if this new user has already been referred by someone.
        existing_referral = Referral.query.filter_by(
            referred_user_id=new_user.id
        ).first()
        if existing_referral:
            raise ReferralException("This user has already been referred.")

        # These values should ideally be configurable.
        REFERRER_REWARD_POINTS = 100
        REFERRED_USER_REWARD_POINTS = 50

        # Use LoyaltyService to award points to both parties.
        self.loyalty_service.add_points(
            referrer.id,
            REFERRER_REWARD_POINTS,
            f"Referred new user: {new_user.email}",
        )
        self.loyalty_service.add_points(
            new_user.id,
            REFERRED_USER_REWARD_POINTS,
            f"Signed up with referral from: {referrer.email}",
        )

        # Create a record of the successful referral.
        referral_record = Referral(
            referrer_id=referrer.id, referred_user_id=new_user.id
        )
        db.session.add(referral_record)

        # Use NotificationService to inform users of their new points.
        self.notification_service.send_referral_credit_notification(
            referrer, new_user, REFERRER_REWARD_POINTS
        )
        self.notification_service.send_welcome_credit_notification(
            new_user, REFERRED_USER_REWARD_POINTS
        )

        db.session.commit()

        return {"success": True, "message": "Referral processed successfully."}

    @staticmethod
    def validate_referral_code(referral_code):
        """Validate if a referral code exists and is valid"""
        try:
            referral_code = InputSanitizer.sanitize_input(referral_code)

            referral = Referral.query.filter_by(referral_code=referral_code).first()
            if not referral:
                return False

            # Check if the referrer is still active
            referrer = User.query.get(referral.referrer_id)
            if not referrer or not referrer.is_active:
                return False

            return True

        except Exception as e:
            MonitoringService.log_error(
                f"Error validating referral code {referral_code}: {str(e)}"
            )
            return False
