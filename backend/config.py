import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from datetime import timedelta  # Added: Import timedelta

# Define basedir for path calculations
basedir = os.path.abspath(os.path.dirname(__file__))
# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration."""

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_BLOCKLIST_ENABLED = True
    JWT_BLOCKLIST_TOKEN_CHECKS = ["access", "refresh"]

    SECRET_KEY = os.environ.get("SECRET_KEY")
    DATABASE_URL = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "app.db"
    )
    FRONTEND_URL = os.environ.get("FRONTEND_URL") or "http://localhost:5173"

    # Admin/staff Session Timeout Configuration
    ADMIN_INACTIVITY_TIMEOUT = timedelta(minutes=5)
    STAFF_INACTIVITY_TIMEOUT = timedelta(minutes=10)
    SESSION_MAX_LIFETIME = timedelta(hours=4)

    # Logging Configuration
    LOG_DIR = os.environ.get("LOG_DIR", "logs")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    USE_JSON_LOGS = os.environ.get("USE_JSON_LOGS", "false").lower() in ["true", "1"]

    # --- IMPLEMENTATION: File Upload Validation ---
    # Max file size: 25 MB
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "svg", "pdf"}
    UPLOAD_FOLDER = os.path.join(basedir, "uploads")

    # --- IMPLEMENTATION: Password Policy ---
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGIT = True
    PASSWORD_REQUIRE_SPECIAL = False

    # Caching
    CACHE_TYPE = "redis"
    CACHE_DEFAULT_TIMEOUT = 3600  # Cache for 1 hour by default
    CACHE_REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # --- Celery Configuration ---
    # The broker URL specifies the connection to your message broker instance (Redis).
    # Celery uses this to send and receive messages for background tasks.
    CELERY_BROKER_URL = (
        os.environ.get("CELERY_BROKER_URL") or "redis://localhost:6379/0"
    )
    CELERY_RESULT_BACKEND = (
        os.environ.get("CELERY_RESULT_BACKEND") or "redis://localhost:6379/0"
    )

    # --- Other configurations ---
    LOG_TO_STDOUT = os.environ.get("LOG_TO_STDOUT")

    # Flask-Security-Too configuration
    SECURITY_PASSWORD_SALT = os.environ.get(
        "SECURITY_PASSWORD_SALT", "a-very-secure-salt"
    )
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = True
    SECURITY_RECOVERABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_TWO_FACTOR_ENABLED_METHODS = ["email", "authenticator"]
    SECURITY_TOTP_ISSUER = "Maison Truvrā"

    # --- Security Settings ---
    # In production, these should be True to ensure secure transmission of cookies.
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Strict"
    REMEMBER_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
    REMEMBER_COOKIE_HTTPONLY = True

    # Additional security headers
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    WTF_CSRF_TIME_LIMIT = 3600

    # CSRF Protection - Flask-WTF uses SECRET_KEY by default but can be set separately
    WTF_CSRF_SECRET_KEY = os.environ.get(
        "WTF_CSRF_SECRET_KEY", "a-different-secret-key"
    )
    WTF_CSRF_ENABLED = True

    # Base URL for generating links (like in product passports)
    BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000")

    # Encryption Key
    ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY") or Fernet.generate_key().decode()

    # Vite Development Server URL
    VITE_DEV_SERVER = os.environ.get("VITE_DEV_SERVER", "http://localhost:5173")


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL", "sqlite:///dev.db")
    # Allow cookies to be sent over HTTP for local development
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")
    WTF_CSRF_ENABLED = False  # Disable CSRF forms in tests for convenience
    SESSION_COOKIE_SECURE = False
    LOG_FILE_PATH = None  # Disable file logging for tests


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    )  # No default for production
    # Enforce secure cookies in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


# Dictionary to map environment names to config classes
config_by_name = dict(dev=DevelopmentConfig, test=TestingConfig, prod=ProductionConfig)
