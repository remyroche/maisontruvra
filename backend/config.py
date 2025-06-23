import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a-default-secret-key-that-is-not-so-secret')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'a-default-jwt-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # --- Security Settings ---
    # In production, these should be True to ensure secure transmission of cookies.
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CSRF Protection - Flask-WTF uses SECRET_KEY by default but can be set separately
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', 'a-different-secret-key')
    WTF_CSRF_ENABLED = True
    
    # Sentry DSN for error reporting
    SENTRY_DSN = os.environ.get('SENTRY_DSN')

    # Base URL for generating links (like in product passports)
    BASE_URL = os.environ.get('BASE_URL', 'http://127.0.0.1:5000')


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
    SENTRY_DSN = None # Disable Sentry for tests


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') # No default for production
    
    # Enforce secure cookies in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    # SENTRY_DSN will be loaded from environment variables

# Dictionary to map environment names to config classes
config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)
