import re
import bleach
from markupsafe import Markup
from backend.services.exceptions import ValidationException

class InputSanitizer:
    """
    Centralized input sanitization to prevent XSS and injection attacks.
    """
    
    @staticmethod
    def sanitize_html(dirty_html):
        """Sanitize HTML content using bleach."""
        if not dirty_html:
            return ""
        
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'h1', 'h2', 'h3']
        allowed_attributes = {}
        
        clean_html = bleach.clean(
            dirty_html,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
        return clean_html
    
    @staticmethod
    def sanitize_string(input_string):
        """Basic string sanitization."""
        if not input_string:
            return ""
        
        # Remove potential script injections
        sanitized = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', input_string, flags=re.IGNORECASE)
        
        # Remove other dangerous patterns
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    @staticmethod
    def validate_email(email):
        """Validate email format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationException("Invalid email format")
        return email.lower().strip()
    
    @staticmethod
    def sanitize_sql_input(input_value):
        """Sanitize input for SQL queries (though parameterized queries are preferred)."""
        if not input_value:
            return ""
        
        # Remove SQL injection patterns
        dangerous_patterns = [
            r'(\b(ALTER|CREATE|DELETE|DROP|EXEC(UTE)?|INSERT|SELECT|UNION|UPDATE)\b)',
            r'(\b(SCRIPT|JAVASCRIPT|VBSCRIPT|ONLOAD|ONERROR)\b)',
            r'([\'\";])',
            r'(\-\-)',
            r'(\/\*|\*\/)'
        ]
        
        sanitized = str(input_value)
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
