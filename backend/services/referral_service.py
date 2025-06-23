from backend.models.user_models import User
from backend.models.referral_models import Referral
from backend.database import db

class ReferralService:
    @staticmethod
    def get_referrer_for_user(user_id: int) -> User | None:
        """
        Finds the user who referred the given user.
        """
        referral_entry = Referral.query.filter_by(referred_user_id=user_id).first()
        if referral_entry:
            return referral_entry.referrer
        return None

    @staticmethod
    def create_referral(referrer_code: str, referred_user_id: int):
        """
        Creates a referral link between two users based on a referral code.
        This would be called during the registration process.
        """
        # Assuming the referral code is the referrer's user ID for simplicity
        try:
            referrer_id = int(referrer_code)
            referrer = User.query.get(referrer_id)
            if not referrer:
                raise ValueError("Invalid referral code.")
        except (ValueError, TypeError):
            raise ValueError("Invalid referral code format.")

        # Check if the user already has a referrer
        if Referral.query.filter_by(referred_user_id=referred_user_id).first():
            # Silently ignore if they already have one, or raise an error
            return

        new_referral = Referral(
            referrer_user_id=referrer.id,
            referred_user_id=referred_user_id
        )
        db.session.add(new_referral)
        db.session.commit()
        return new_referral
