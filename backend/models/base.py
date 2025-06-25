
from backend.database import db
from datetime import datetime

class SoftDeleteMixin:
    """
    A mixin that adds soft delete functionality to a model.
    """
    is_deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def soft_delete(self):
        """Mark the record as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        db.session.add(self)

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        db.session.add(self)
        
    @classmethod
    def query_active(cls):
        """Returns a query for non-deleted records of this model."""
        return cls.query.filter_by(is_deleted=False)

    @classmethod
    def query_with_deleted(cls):
        """Returns a query for all records of this model, including deleted ones."""
        return cls.query


class BaseModel(db.Model):
    """
    An abstract base model that provides common columns.
    Models inheriting from this should define their own `to_dict` methods
    for serialization, as context can vary greatly between models.
    """
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
