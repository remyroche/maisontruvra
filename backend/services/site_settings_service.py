import logging
from backend.database import db
from backend.models.utility_models import Setting
from backend.services.monitoring_service import MonitoringService
from backend.utils.decorators import roles_required, permissions_required
from backend.utils.input_sanitizer import InputSanitizer
from flask import current_app


logger = logging.getLogger(__name__)

class SiteSettingsService:
    """
    Service pour gérer les paramètres globaux du site stockés dans la base de données.
    """

    @staticmethod
    @roles_required
    def get_all_settings(self):
        """ Retrieves all settings from the database. """
        settings = Setting.query.all()
        return {setting.key: setting.value for setting in settings}

    @staticmethod
    @roles_required
    def update_settings(settings_data: dict):
        """
        Updates multiple site settings. Assumes data is already sanitized.
        """
        for key, value in settings_data.items():
            setting = Setting.query.filter_by(key=key).first()
            
            # The value from request.json is already sanitized by middleware.
            # We can just convert to string for database storage.
            processed_value = str(value)

            if setting:
                setting.value = processed_value
            else:
                # Create a new setting if it doesn't exist
                new_setting = SiteSetting(key=key, value=processed_value)
                db.session.add(new_setting)
        
        db.session.commit()
        current_app.logger.info(f"Site settings updated: {list(settings_data.keys())}")
        return True


    @staticmethod
    @roles_required
    def get_setting(key: str, default=None):
        setting = Setting.query.filter_by(key=key).first()
        return setting.value if setting else None
