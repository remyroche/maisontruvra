from backend.models import db
from backend.models.admin_audit_models import AdminAuditLog
from backend.models.user_models import User
from flask import current_app

class AuditLogService:
    """
    Service class for handling admin audit log operations.
    """

    @staticmethod
    def create_log(admin_user_id: int, action: str, details: str = ""):
        """
        Creates and saves a new audit log entry.

        This method should be called from other services whenever a significant
        action is performed by an admin.

        :param admin_user_id: The ID of the admin user performing the action.
        :param action: A short description of the action (e.g., 'User Deletion').
        :param details: A more detailed description of the event (e.g., 'Deleted user with email a@b.com').
        """
        try:
            log_entry = AdminAuditLog(
                admin_user_id=admin_user_id,
                action=action,
                details=details
            )
            db.session.add(log_entry)
            db.session.commit()
            current_app.logger.info(f"Audit log created: Admin {admin_user_id} -> {action}")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to create audit log: {e}")


    @staticmethod
    def get_logs(admin_id=None):
        """
        Retrieves audit log entries, optionally filtering by admin user.

        :param admin_id: Optional ID of an admin to filter logs by.
        :return: A list of audit log entries.
        """
        try:
            query = AdminAuditLog.query.join(User, AdminAuditLog.admin_user_id == User.id)\
                                     .options(db.joinedload(AdminAuditLog.admin_user))\
                                     .order_by(AdminAuditLog.timestamp.desc())

            if admin_id:
                query = query.filter(AdminAuditLog.admin_user_id == admin_id)

            logs = query.all()
            return [log.to_dict() for log in logs]
        except Exception as e:
            current_app.logger.error(f"Failed to retrieve audit logs: {e}")
            return []



