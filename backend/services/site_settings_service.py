"""
Service layer for managing site-wide settings.
"""

import logging
from flask import current_app

from ..extensions import db, cache
from ..models.utility_models import Setting
from ..utils.decorators import roles_required
from ..utils.cache_helpers import get_site_settings_key, clear_site_settings_cache

logger = logging.getLogger(__name__)


class SiteSettingsService:
    """
    Service to manage global site settings stored in the database,
    with a caching layer for performance.
    """

    @staticmethod
    def get_all_settings_cached():
        """
        Retrieves all site settings as a dictionary, using cache.
        Settings are long-lived in cache as they change infrequently.
        """
        cache_key = get_site_settings_key()
        settings = cache.get(cache_key)
        if settings is None:
            current_app.logger.debug("Cache miss for site settings. Fetching from DB.")
            settings_models = Setting.query.all()
            settings = {s.key: s.value for s in settings_models}
            cache.set(cache_key, settings, timeout=86400)  # Cache for 24 hours
        else:
            current_app.logger.debug("Cache hit for site settings.")
        return settings

    @staticmethod
    def get_setting(key: str, default=None):
        """
        Retrieves a single setting value by its key from the cached dictionary.
        This is highly performant as it avoids a database call for each key.
        """
        settings = SiteSettingsService.get_all_settings_cached()
        return settings.get(key, default)

    @staticmethod
    @roles_required("Admin")  # Protect this operation
    def update_settings(settings_data: dict):
        """
        Updates multiple site settings, invalidates the cache, and logs the action.
        Assumes input data is already sanitized by middleware or controllers.
        """
        for key, value in settings_data.items():
            setting = Setting.query.filter_by(key=key).first()

            # Convert value to string for consistent database storage.
            processed_value = str(value)

            if setting:
                setting.value = processed_value
            else:
                # Create a new setting if it doesn't exist
                setting = Setting(key=key, value=processed_value)
                db.session.add(setting)

        db.session.commit()

        # CRITICAL: Invalidate the cache after updating the database.
        clear_site_settings_cache()

        current_app.logger.info(
            f"Site settings updated by admin: {list(settings_data.keys())}"
        )
        return True

    @staticmethod
    @roles_required("Admin")  # Also protect this direct DB access method
    def get_all_settings_from_db():
        """
        Retrieves all settings directly from the database, bypassing the cache.
        Useful for admin panels that need to show the absolute latest state.
        """
        settings = Setting.query.all()
        return {setting.key: setting.value for setting in settings}
