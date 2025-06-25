"""
Centralized logging configuration for the application.
This module defines all loggers used throughout the application to ensure consistency.
"""

import logging
from logging.handlers import TimedRotatingFileHandler
import os
import json

# Create loggers
app_logger = logging.getLogger('app')
security_logger = logging.getLogger('security')
database_logger = logging.getLogger('database')
api_logger = logging.getLogger('api')

# Set default levels
security_logger.setLevel(logging.INFO)
database_logger.setLevel(logging.INFO)

class JsonFormatter(logging.Formatter):
    """
    Formats log records as JSON strings.
    """
    def format(self, record):
        log_object = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
        }
        if record.exc_info:
            log_object['exc_info'] = self.formatException(record.exc_info)
        return json.dumps(log_object)

def setup_logging(app):
    """
    Configures comprehensive logging for the Flask application.
    """
    if not app.debug and not app.testing:
        # Get configuration from app config
        log_dir = app.config.get('LOG_DIR', 'logs')
        log_level_str = app.config.get('LOG_LEVEL', 'INFO').upper()
        log_level = getattr(logging, log_level_str, logging.INFO)
        use_json_formatter = app.config.get('USE_JSON_LOGS', False)

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # File Handler with daily rotation
        file_handler = TimedRotatingFileHandler(
            os.path.join(log_dir, 'app.log'), when='midnight', interval=1, backupCount=30
        )

        if use_json_formatter:
            formatter = JsonFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            )
        
        file_handler.setFormatter(formatter)
        
        # Console handler for simple output
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        # Configure all loggers
        for logger in [app.logger, app_logger, security_logger, database_logger, api_logger]:
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            logger.setLevel(log_level)
        
        app.logger.info('Application Logging Started')

__all__ = ['app_logger', 'security_logger', 'database_logger', 'api_logger', 'setup_logging']