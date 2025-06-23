from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging

db = SQLAlchemy()
migrate = Migrate()
db_logger = logging.getLogger('database')

def setup_database_security(app):
    """Setup database security configurations."""

    @app.before_request
    def log_db_queries():
        """Log database queries for monitoring."""
        if app.config.get('DEBUG'):
            db_logger.debug(f"Database query from {request.endpoint}")

    # Configure SQLAlchemy engine options for security
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'check_same_thread': False,
        }
    }