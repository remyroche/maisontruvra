import logging
from backend.database import db
from backend.models.utility_models import Setting
from backend.services.monitoring_service import MonitoringService
from backend.utils.decorators import roles_required, permissions_required

logger = logging.getLogger(__name__)

class SiteSettingsService:
    """
    Service pour gérer les paramètres globaux du site stockés dans la base de données.
    """

    @staticmethod
    @roles_required
    def get_all_settings() -> dict:
        """
        Récupère tous les paramètres du site et les retourne sous forme de dictionnaire.
        """
        try:
            settings = Setting.query.all()
            # Convertit la liste d'objets Setting en un dictionnaire clé-valeur
            return {setting.key: setting.value for setting in settings}
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des paramètres du site : {e}", exc_info=True)
            # Retourne un dictionnaire vide en cas d'erreur
            return {}

    @staticmethod
    @roles_required
    def update_settings(settings_data: dict):
        """
        Met à jour plusieurs paramètres du site à partir d'un dictionnaire.
        Crée de nouveaux paramètres s'ils n'existent pas.
        
        Args:
            settings_data: Un dictionnaire où les clés sont les noms des paramètres
                           et les valeurs sont les nouvelles valeurs.
                           
        Raises:
            ValueError: Si les données fournies ne sont pas un dictionnaire.
        """
        if not isinstance(settings_data, dict):
            raise ValueError("Les données des paramètres doivent être un dictionnaire.")

        try:
            for key, value in settings_data.items():
                # Cherche si le paramètre existe déjà
                setting = Setting.query.filter_by(key=key).first()
                if setting:
                    # Met à jour la valeur s'il existe
                    setting.value = str(value) # S'assurer que la valeur est une chaîne
                else:
                    # Crée un nouveau paramètre s'il n'existe pas
                    setting = Setting(key=key, value=str(value))
                    db.session.add(setting)
                
                logger.info(f"Paramètre du site mis à jour : {key} = {value}")

            db.session.commit()
            MonitoringService.log_info("Les paramètres du site ont été mis à jour avec succès.", "SiteSettingsService")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la mise à jour des paramètres du site : {e}", exc_info=True)
            MonitoringService.log_error("Échec de la mise à jour des paramètres du site.", "SiteSettingsService")
            # Propage l'exception pour que la route puisse la gérer
            raise

    @staticmethod
    @roles_required
    def get_setting(key: str, default=None):
        """
        Récupère la valeur d'un paramètre spécifique.
        
        Args:
            key: La clé du paramètre à récupérer.
            default: La valeur à retourner si la clé n'est pas trouvée.
            
        Returns:
            La valeur du paramètre ou la valeur par défaut.
        """
        setting = Setting.query.filter_by(key=key).first()
        return setting.value if setting else default
