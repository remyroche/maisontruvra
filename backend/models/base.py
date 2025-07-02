"""
This module defines the base model and common mixins for all SQLAlchemy models.
"""
from backend.extensions import db
from sqlalchemy import event
from sqlalchemy.orm import Query

class SoftDeleteQuery(Query):
    """
    A custom query class that automatically filters for `is_deleted = False`
    unless explicitly told otherwise.
    """
    def get(self, ident):
        # Override get() to also apply the is_deleted filter.
        return self.with_for_update(read=True).filter_by(is_deleted=False).get(ident)

    def __iter__(self):
        # Apply the filter for all iteration-based queries (e.g., .all(), .first())
        return super(SoftDeleteQuery, self.filter_by(is_deleted=False)).__iter__()

class SoftDeleteMixin:
    """
    A mixin that adds soft-delete capabilities to a model.
    It includes an `is_deleted` column and sets up a custom query class
    to automatically exclude soft-deleted records from queries.
    """
    is_deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)
    query_class = SoftDeleteQuery

    def soft_delete(self):
        """Marks the instance as deleted."""
        self.is_deleted = True
        db.session.add(self)

    def restore(self):
        """Restores a soft-deleted instance."""
        self.is_deleted = False
        db.session.add(self)

class TimestampMixin:
    """
    A mixin that adds `created_at` and `updated_at` timestamp columns
    to a model, which are automatically managed.
    """
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)

class BaseModel(db.Model):
    """
    Base model for all other models in the application.
    It includes an `id` primary key and can be extended with mixins.
    """
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
