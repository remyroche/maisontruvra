from backend.database import db
from backend.models.user_models import User
from backend.models.referral_models import Referral
from backend.services.exceptions import NotFoundException, ValidationException, ServiceError
from backend.utils.sanitization import sanitize_input
from backend.services.audit_log_service import AuditLogService
from flask import current_app
from flask_jwt_extended import get_jwt_identity
import secrets
import string
from datetime import datetime


class ReferralService:
    """Service for managing user referrals and referral rewards"""
    
    def __init__(self, session=None):
        self.session = session or db.session
    
    @staticmethod
    def generate_referral_code(user_id):
        """Generate a unique referral code for a user"""
        try:
            user_id = sanitize_input(user_id)
            
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
                code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
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
                    created_at=datetime.utcnow()
                )
                db.session.add(referral)
            
            db.session.commit()
            
            # Log the action
            AuditLogService.log_action(
                user_id=user_id,
                action="GENERATE_REFERRAL_CODE",
                resource_type="REFERRAL",
                resource_id=referral.id,
                details=f"Generated referral code: {code}"
            )
            
            current_app.logger.info(f"Generated referral code {code} for user {user_id}")
            return code
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error generating referral code for user {user_id}: {str(e)}")
            raise ServiceError(f"Failed to generate referral code: {str(e)}")
    
    @staticmethod
    def apply_referral_code(user_id, referral_code):
        """Apply a referral code when a user signs up"""
        try:
            user_id = sanitize_input(user_id)
            referral_code = sanitize_input(referral_code)
            
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
            referral.status = 'pending'
            referral.referred_at = datetime.utcnow()
            
            db.session.commit()
            
            # Log the action
            AuditLogService.log_action(
                user_id=user_id,
                action="APPLY_REFERRAL_CODE",
                resource_type="REFERRAL",
                resource_id=referral.id,
                details=f"Applied referral code: {referral_code}"
            )
            
            current_app.logger.info(f"User {user_id} applied referral code {referral_code}")
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error applying referral code {referral_code} for user {user_id}: {str(e)}")
            raise ServiceError(f"Failed to apply referral code: {str(e)}")
    
    @staticmethod
    def complete_referral(user_id):
        """Complete a referral when the referred user makes their first purchase"""
        try:
            user_id = sanitize_input(user_id)
            
            # Find the referral record for this user
            referral = Referral.query.filter_by(referred_id=user_id, status='pending').first()
            if not referral:
                return False  # No pending referral found
            
            # Mark referral as completed
            referral.status = 'completed'
            referral.completed_at = datetime.utcnow()
            
            db.session.commit()
            
            # Log the action
            AuditLogService.log_action(
                user_id=user_id,
                action="COMPLETE_REFERRAL",
                resource_type="REFERRAL",
                resource_id=referral.id,
                details=f"Completed referral for user {user_id}"
            )
            
            current_app.logger.info(f"Completed referral for user {user_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error completing referral for user {user_id}: {str(e)}")
            raise ServiceError(f"Failed to complete referral: {str(e)}")
    
    @staticmethod
    def get_user_referrals(user_id):
        """Get all referrals made by a user"""
        try:
            user_id = sanitize_input(user_id)
            
            # Verify user exists
            user = User.query.get(user_id)
            if not user:
                raise NotFoundException("User not found")
            
            referrals = Referral.query.filter_by(referrer_id=user_id).all()
            
            result = []
            for referral in referrals:
                referred_user = User.query.get(referral.referred_id) if referral.referred_id else None
                result.append({
                    'id': referral.id,
                    'referral_code': referral.referral_code,
                    'referred_user': {
                        'id': referred_user.id,
                        'email': referred_user.email
                    } if referred_user else None,
                    'status': referral.status,
                    'created_at': referral.created_at.isoformat() if referral.created_at else None,
                    'referred_at': referral.referred_at.isoformat() if referral.referred_at else None,
                    'completed_at': referral.completed_at.isoformat() if referral.completed_at else None
                })
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error getting referrals for user {user_id}: {str(e)}")
            raise ServiceError(f"Failed to get referrals: {str(e)}")
    
    @staticmethod
    def get_referral_stats(user_id):
        """Get referral statistics for a user"""
        try:
            user_id = sanitize_input(user_id)
            
            # Verify user exists
            user = User.query.get(user_id)
            if not user:
                raise NotFoundException("User not found")
            
            total_referrals = Referral.query.filter_by(referrer_id=user_id).filter(Referral.referred_id.isnot(None)).count()
            completed_referrals = Referral.query.filter_by(referrer_id=user_id, status='completed').count()
            pending_referrals = Referral.query.filter_by(referrer_id=user_id, status='pending').count()
            
            # Get user's referral code
            referral_record = Referral.query.filter_by(referrer_id=user_id).first()
            referral_code = referral_record.referral_code if referral_record else None
            
            return {
                'referral_code': referral_code,
                'total_referrals': total_referrals,
                'completed_referrals': completed_referrals,
                'pending_referrals': pending_referrals
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting referral stats for user {user_id}: {str(e)}")
            raise ServiceError(f"Failed to get referral stats: {str(e)}")
    
    @staticmethod
    def validate_referral_code(referral_code):
        """Validate if a referral code exists and is valid"""
        try:
            referral_code = sanitize_input(referral_code)
            
            referral = Referral.query.filter_by(referral_code=referral_code).first()
            if not referral:
                return False
            
            # Check if the referrer is still active
            referrer = User.query.get(referral.referrer_id)
            if not referrer or not referrer.is_active:
                return False
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error validating referral code {referral_code}: {str(e)}")
            return False