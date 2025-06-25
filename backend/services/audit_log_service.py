from backend.database import db
from backend.models.admin_audit_models import AdminAuditLog
from backend.models.user_models import User
from flask import current_app
from datetime import datetime

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
            # Corrected the variable name from staff_user_id to admin_user_id
            log_entry = AdminAuditLog(admin_user_id=admin_user_id, action=action, details=details)
            db.session.add(log_entry)
            db.session.commit()
            current_app.logger.info(f"Audit log created: Admin {admin_user_id} -> {action}")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to create audit log: {e}")

    @staticmethod
    def get_logs(page=1, per_page=20, date_filter=None):
        """
        Retrieves paginated audit log entries, optionally filtering by date.
        """
        try:
            query = AdminAuditLog.query.join(User, AdminAuditLog.admin_user_id == User.id)\
                                     .options(db.joinedload(AdminAuditLog.admin_user))\
                                     .order_by(AdminAuditLog.timestamp.desc())

            if date_filter:
                try:
                    # Expecting date in 'YYYY-MM-DD' format
                    filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                    query = query.filter(db.func.date(AdminAuditLog.timestamp) == filter_date)
                except ValueError:
                    # Ignore invalid date formats
                    pass

            paginated_logs = query.paginate(page=page, per_page=per_page, error_out=False)
            
            return {
                "logs": [log.to_dict() for log in paginated_logs.items],
                "total": paginated_logs.total,
                "pages": paginated_logs.pages,
                "current_page": paginated_logs.page,
                "has_next": paginated_logs.has_next,
                "has_prev": paginated_logs.has_prev,
            }
        except Exception as e:
            current_app.logger.error(f"Failed to retrieve audit logs: {e}")
            return {"logs": [], "total": 0, "pages": 0}
