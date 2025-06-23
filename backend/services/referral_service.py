from backend.models.user_models import User
from backend.models.referral_models import Referral
from backend.database import db

class ReferralService:
    @staticmethod
    def get_referrer_for_user(user_id: int) -> User | None:
        """
        Finds and returns the user who referred the given user.
        """
        referral_entry = Referral.query.filter_by(referred_user_id=user_id).first()
        return referral_entry.referrer if referral_entry else None

    @staticmethod
    def create_referral(referrer_code: str, referred_user_id: int):
        """
        Creates a referral link between two users based on a referral code.
        This should be called during the registration process of the new user.
        """
        if not referrer_code:
            # No referral code provided, so we do nothing.
            return None

        # Assuming the referral code is the referrer's user ID for simplicity
        try:
            referrer_id = int(referrer_code)
            referrer = User.query.get(referrer_id)
            if not referrer:
                raise ValueError("Le code de parrainage est invalide.")
        except (ValueError, TypeError):
            raise ValueError("Le format du code de parrainage est invalide.")

        # Ensure the referred user doesn't already have a referrer
        existing_referral = Referral.query.filter_by(referred_user_id=referred_user_id).first()
        if existing_referral:
            # It's better to raise an error to let the caller know, rather than failing silently.
            # The API route can choose to ignore this specific error if needed.
            raise ValueError("Cet utilisateur a déjà été parrainé.")

        new_referral = Referral(
            referrer_user_id=referrer.id,
            referred_user_id=referred_user_id
        )
        db.session.add(new_referral)
        
        # The calling function (e.g., AuthService.register_user) is responsible 
        # for the db.session.commit() call to ensure an atomic transaction.
        return new_referral
