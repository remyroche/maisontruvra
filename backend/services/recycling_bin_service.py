from backend.models import (
    Product,
    Category,
    Collection,
    User,
    B2BAccount,
    BlogPost,
    Order,
    Review,
    AdminAuditLog,
)
from backend.database import db
from backend.services.audit_log_service import AuditLogService
from flask_login import current_user

# A mapping from a string identifier to the corresponding model class.
# This allows the service to be generic across different types of items.
MODEL_MAP = {
    "product": Product,
    "category": Category,
    "collection": Collection,
    "user": User,
    "b2b_account": B2BAccount,
    "blog_post": BlogPost,
    "order": Order,
    "review": Review,
}

audit_log_service = AuditLogService()


class RecyclingBinService:
    """
    Service layer for managing soft-deleted items (Recycling Bin).
    """

    def get_soft_deleted_items(self):
        """
        Retrieves all items that have been soft-deleted from the database.

        It iterates through all models that support soft deletion.
        """
        all_deleted_items = []
        for model_name, model_class in MODEL_MAP.items():
            # Query for items where 'deleted_at' is not null.
            deleted_items = model_class.query.filter(
                model_class.deleted_at.isnot(None)
            ).all()
            for item in deleted_items:
                # Create a consistent identifier for different models.
                identifier = (
                    getattr(item, "name", None)
                    or getattr(item, "title", None)
                    or getattr(item, "email", None)
                    or f"ID: {item.id}"
                )
                all_deleted_items.append(
                    {
                        "item_id": item.id,
                        "item_type": model_name,
                        "identifier": identifier,
                        "deleted_at": item.deleted_at.isoformat()
                        if item.deleted_at
                        else None,
                    }
                )
        return all_deleted_items

    def restore_item(self, item_type: str, item_id: int):
        """
        Restores a soft-deleted item by setting its 'deleted_at' timestamp to NULL.
        """
        model_class = MODEL_MAP.get(item_type)
        if not model_class:
            raise ValueError("Invalid item type specified.")

        item = model_class.query.filter_by(id=item_id).first()
        if not item:
            raise ValueError("Item not found.")

        item.restore()
        db.session.commit()

        audit_log_service.add_entry(
            f"Restored {item_type} '{getattr(item, 'name', item.id)}'",
            user_id=current_user.id,
            target_type=item_type,
            target_id=item_id,
            action="restore",
        )
        return item

    def hard_delete_item(self, item_type: str, item_id: int):
        """
        Permanently deletes an item from the database.
        """
        model_class = MODEL_MAP.get(item_type)
        if not model_class:
            raise ValueError("Invalid item type specified.")

        item = model_class.query.filter_by(id=item_id).first()
        if not item:
            raise ValueError("Item not found.")

        item_identifier = getattr(item, "name", item.id)
        db.session.delete(item)
        db.session.commit()

        audit_log_service.add_entry(
            f"Hard-deleted {item_type} '{item_identifier}'",
            user_id=current_user.id,
            target_type=item_type,
            target_id=item_id,
            action="hard_delete",
        )

    def get_deletion_logs(self, item_type: str, item_id: int):
        """
        Retrieves the audit logs related to an item's deletion.
        """
        logs = (
            AdminAuditLog.query.filter(
                AdminAuditLog.target_type == item_type,
                AdminAuditLog.target_id == item_id,
                AdminAuditLog.action.in_(["soft_delete", "hard_delete", "restore"]),
            )
            .order_by(AdminAuditLog.timestamp.desc())
            .all()
        )

        return [log.to_dict() for log in logs]
