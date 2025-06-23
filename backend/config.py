import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a-default-secret-key-that-is-not-so-secret')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'a-default-jwt-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    FRONTEND_URL = os.environ.get('FRONTEND_URL') or 'http://localhost:5173'

    
    # --- Security Settings ---
    # In production, these should be True to ensure secure transmission of cookies.
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    REMEMBER_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Additional security headers
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    WTF_CSRF_TIME_LIMIT = 3600
    
    # CSRF Protection - Flask-WTF uses SECRET_KEY by default but can be set separately
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', 'a-different-secret-key')
    WTF_CSRF_ENABLED = True
    
    # Base URL for generating links (like in product passports)
    BASE_URL = os.environ.get('BASE_URL', 'http://127.0.0.1:5000')

    # Encryption Key
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or Fernet.generate_key().decode()

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL', 'sqlite:///dev.db')
    # Allow cookies to be sent over HTTP for local development
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL', 'sqlite:///:memory:')
    WTF_CSRF_ENABLED = False # Disable CSRF forms in tests for convenience
    SESSION_COOKIE_SECURE = False
    LOG_FILE_PATH = None # Disable file logging for tests


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') # No default for production
    # Enforce secure cookies in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    REMEMBER_COOKIE_SECURE = True

# Dictionary to map environment names to config classes
config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)
