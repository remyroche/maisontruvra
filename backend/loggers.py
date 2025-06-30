"""
Centralized logging configuration for the application.
This module defines all loggers used throughout the application to ensure consistency.
"""

import logging
from logging.handlers import TimedRotatingFileHandler
import os
import json
from logging.config import dictConfig
from flask import g, request


# Create loggers
app_logger = logging.getLogger('app')
security_logger = logging.getLogger('security')
database_logger = logging.getLogger('database')
api_logger = logging.getLogger('api')

# Set default levels
security_logger.setLevel(logging.INFO)
database_logger.setLevel(logging.INFO)


class RequestIDFilter(logging.Filter):
    """
    A logging filter that injects the request ID into log records.

    This class is used to add contextual information from the request,
    specifically a unique request ID and the request endpoint, to each log
    entry. This is invaluable for tracing and debugging.
    """
    def filter(self, record):
        """
        Adds the request ID and endpoint to the log record.

        If a request ID is present in Flask's 'g' object, it's added
        to the log record. Otherwise, a default value is used.
        """
        record.request_id = g.get('request_id', 'no-request-id')
        record.endpoint = request.path if request else 'not-in-request-context'
        return True

# Configuration for the application's logging
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'request_id_filter': {
            '()': RequestIDFilter,
        }
    },
    'formatters': {
        'standard': {
            # Added %(request_id)s and %(endpoint)s to the log format
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s [request_id:%(request_id)s endpoint:%(endpoint)s]'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'filters': ['request_id_filter'], # Apply the filter to this handler
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'app.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
            'filters': ['request_id_filter'], # Apply the filter to this handler
        },
        'security': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'security.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
            'filters': ['request_id_filter'], # Apply the filter to this handler
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        },
        'app_logger': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False
        },
        'security_logger': {
            'handlers': ['console', 'security'],
            'level': 'WARNING',
            'propagate': False
        }
    }
}

def setup_logging():
    """Applies the logging configuration."""
    dictConfig(LOGGING_CONFIG)



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
