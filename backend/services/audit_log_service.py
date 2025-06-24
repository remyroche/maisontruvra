from flask import request
from flask_jwt_extended import get_jwt_identity
from backend.database import db
from backend.models.audit_models import AuditLog
from .. import celery # Assuming celery is initialized in __init__.py

class AuditLogService:
    def log(admin_user_id, action, target_type=None, target_id=None, details=None):
        """
        Logs an admin action. This is now a Celery task to ensure
        that logging does not slow down the user's request.
        
        Args:
            admin_user_id (int): The ID of the admin performing the action.
            action (str): A description of the action.
            target_type (str, optional): The model name of the object being affected.
            target_id (int, optional): The ID of the object being affected.
            details (dict, optional): A JSON-serializable dict with extra info.
        """
        try:
            log_entry = AdminAuditLog(
                admin_user_id=admin_user_id,
                action=action,
                target_type=target_type,
                target_id=target_id,
                details=details,
                ip_address=request.remote_addr
            )
            db.session.add(log_entry)
            db.session.commit()
        except Exception as e:
            # If logging fails, we don't want to crash the main application.
            # We would log this failure to a separate, more robust logging system.
            print(f"CRITICAL: Audit logging failed: {e}")

    
    @staticmethod
    def log_action(action: str, target_id: int = None, details: dict = None):
        """
        Creates a new audit log entry. This should be called by other services
        after a sensitive action has been successfully performed.

        Args:
            action (str): A clear, machine-readable string describing the action
                          (e.g., 'ADMIN_CREATE_DELIVERY_METHOD').
            target_id (int, optional): The ID of the entity that was acted upon.
            details (dict, optional): A JSON-serializable dictionary containing
                                      relevant data about the action, such as
                                      the changes made.
        """
        try:
            # Get the ID of the currently logged-in admin/staff user
            performed_by_id = get_jwt_identity()
            if not performed_by_id:
                # This should ideally not happen if the endpoint is protected,
                # but it's a safe fallback.
                raise ValueError("Impossible de logger une action pour un utilisateur non identifié.")

            # Get the IP address of the user performing the action
            ip_address = request.remote_addr

            log_entry = AuditLog(
                user_id=performed_by_id,
                action=action,
                target_id=target_id,
                details=details,
                ip_address=ip_address
            )
            db.session.add(log_entry)
            # The calling service is responsible for the final db.session.commit()
            # to ensure the log is part of the same atomic transaction.
        except Exception as e:
            # If logging fails, we should not crash the primary operation.
            # Instead, log the logging failure itself to the system logger.
            from flask import current_app
            current_app.logger.error(f"FATAL: Échec de l'enregistrement du journal d'audit: {e}")

    @staticmethod
    def get_all_logs_paginated(page: int, per_page: int, filters: dict = None):
        """
        Retrieves a paginated list of audit logs for the admin panel.
        """
        query = AuditLog.query

        # The existing audit log route already handles filtering, so this
        # service method can be expanded later if needed.

        return query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
