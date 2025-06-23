
from backend.database import db
from datetime import datetime

class BaseModel(db.Model):
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self, context='basic'):
        """
        Convert model to dictionary with context-aware serialization.
        
        Contexts:
        - 'basic': Basic fields only
        - 'public': Safe for public API
        - 'admin': All fields for admin interface
        - 'full': All fields including relationships
        """
        result = {}
        
        # Get basic fields
        basic_fields = getattr(self, '_basic_fields', [])
        public_fields = getattr(self, '_public_fields', [])
        admin_fields = getattr(self, '_admin_fields', [])
        sensitive_fields = getattr(self, '_sensitive_fields', [])
        
        # Determine which fields to include
        if context == 'basic':
            allowed_fields = basic_fields
        elif context == 'public':
            allowed_fields = basic_fields + public_fields
        elif context == 'admin':
            allowed_fields = basic_fields + public_fields + admin_fields
        elif context == 'full':
            allowed_fields = basic_fields + public_fields + admin_fields
        else:
            allowed_fields = basic_fields
        
        # Add basic timestamp fields
        allowed_fields.extend(['id', 'created_at', 'updated_at'])
        
        # Exclude sensitive fields unless admin context
        if context != 'admin':
            allowed_fields = [f for f in allowed_fields if f not in sensitive_fields]
        
        for field in allowed_fields:
            if hasattr(self, field):
                value = getattr(self, field)
                if isinstance(value, datetime):
                    result[field] = value.isoformat()
                elif hasattr(value, 'value'):  # Enum
                    result[field] = value.value
                else:
                    result[field] = value
        
        # Handle relationships for 'full' context
        if context == 'full':
            relationships = getattr(self, '_relationships', [])
            for rel_name in relationships:
                if hasattr(self, rel_name):
                    rel_value = getattr(self, rel_name)
                    if rel_value is not None:
                        if isinstance(rel_value, list):
                            result[rel_name] = [item.to_dict('public') for item in rel_value]
                        else:
                            result[rel_name] = rel_value.to_dict('public')
        
        return result
