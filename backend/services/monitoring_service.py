# This service contains the logic to read and parse the log file.
# It also provides centralized logging functionality for all services.

import os
from flask import current_app
from backend.loggers import app_logger, security_logger, database_logger, api_logger
import logging
from typing import Optional, Any, Dict
from functools import wraps

class MonitoringService:
    """
    Service for providing monitoring data, such as reading recent logs
    from the application's log file, and centralized logging functionality.
    """
    
    # Centralized Logging Methods
    @staticmethod
    def log_info(message: str, service_name: str = None, extra_data: Dict[str, Any] = None):
        """Log informational messages with service context."""
        formatted_message = MonitoringService._format_message(message, service_name, extra_data)
        app_logger.info(formatted_message)
    
    @staticmethod
    def log_warning(message: str, service_name: str = None, extra_data: Dict[str, Any] = None):
        """Log warning messages with service context."""
        formatted_message = MonitoringService._format_message(message, service_name, extra_data)
        app_logger.warning(formatted_message)
    
    @staticmethod
    def log_error(message: str, service_name: str = None, extra_data: Dict[str, Any] = None, exc_info: bool = False):
        """Log error messages with service context."""
        formatted_message = MonitoringService._format_message(message, service_name, extra_data)
        app_logger.error(formatted_message, exc_info=exc_info)
    
    @staticmethod
    def log_critical(message: str, service_name: str = None, extra_data: Dict[str, Any] = None, exc_info: bool = False):
        """Log critical messages with service context."""
        formatted_message = MonitoringService._format_message(message, service_name, extra_data)
        app_logger.critical(formatted_message, exc_info=exc_info)
    
    @staticmethod
    def log_debug(message: str, service_name: str = None, extra_data: Dict[str, Any] = None):
        """Log debug messages with service context."""
        formatted_message = MonitoringService._format_message(message, service_name, extra_data)
        app_logger.debug(formatted_message)
    
    # Specialized logging methods
    @staticmethod
    def log_security_event(message: str, service_name: str = None, extra_data: Dict[str, Any] = None, level: str = 'INFO'):
        """Log security-related events."""
        formatted_message = MonitoringService._format_message(message, service_name, extra_data)
        if level.upper() == 'WARNING':
            security_logger.warning(formatted_message)
        elif level.upper() == 'ERROR':
            security_logger.error(formatted_message)
        elif level.upper() == 'CRITICAL':
            security_logger.critical(formatted_message)
        else:
            security_logger.info(formatted_message)
    
    @staticmethod
    def log_database_operation(message: str, service_name: str = None, extra_data: Dict[str, Any] = None, level: str = 'INFO'):
        """Log database operations."""
        formatted_message = MonitoringService._format_message(message, service_name, extra_data)
        if level.upper() == 'WARNING':
            database_logger.warning(formatted_message)
        elif level.upper() == 'ERROR':
            database_logger.error(formatted_message)
        elif level.upper() == 'CRITICAL':
            database_logger.critical(formatted_message)
        else:
            database_logger.info(formatted_message)
    
    @staticmethod
    def log_api_request(message: str, service_name: str = None, extra_data: Dict[str, Any] = None, level: str = 'INFO'):
        """Log API requests and responses."""
        formatted_message = MonitoringService._format_message(message, service_name, extra_data)
        if level.upper() == 'WARNING':
            api_logger.warning(formatted_message)
        elif level.upper() == 'ERROR':
            api_logger.error(formatted_message)
        elif level.upper() == 'CRITICAL':
            api_logger.critical(formatted_message)
        else:
            api_logger.info(formatted_message)
    
    @staticmethod
    def _format_message(message: str, service_name: str = None, extra_data: Dict[str, Any] = None) -> str:
        """Format log message with service context and extra data."""
        formatted_parts = []
        
        if service_name:
            formatted_parts.append(f"[{service_name}]")
        
        formatted_parts.append(message)
        
        if extra_data:
            extra_str = " | ".join([f"{k}={v}" for k, v in extra_data.items()])
            formatted_parts.append(f"| {extra_str}")
        
        return " ".join(formatted_parts)
    
    @staticmethod
    def log_service_operation(operation: str, service_name: str, success: bool = True, 
                            duration_ms: Optional[float] = None, extra_data: Dict[str, Any] = None):
        """Log service operations with standardized format."""
        status = "SUCCESS" if success else "FAILED"
        message = f"Operation '{operation}' {status}"
        
        if duration_ms is not None:
            message += f" (took {duration_ms:.2f}ms)"
        
        log_data = extra_data or {}
        log_data['operation'] = operation
        log_data['status'] = status
        
        if duration_ms is not None:
            log_data['duration_ms'] = duration_ms
        
        if success:
            MonitoringService.log_info(message, service_name, log_data)
        else:
            MonitoringService.log_error(message, service_name, log_data)
    
    # Decorator for automatic service operation logging
    @staticmethod
    def log_service_call(service_name: str, operation_name: str = None):
        """Decorator to automatically log service method calls."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                import time
                op_name = operation_name or func.__name__
                start_time = time.time()
                
                try:
                    MonitoringService.log_debug(f"Starting operation '{op_name}'", service_name)
                    result = func(*args, **kwargs)
                    duration_ms = (time.time() - start_time) * 1000
                    MonitoringService.log_service_operation(op_name, service_name, True, duration_ms)
                    return result
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    MonitoringService.log_service_operation(
                        op_name, service_name, False, duration_ms, 
                        {'error': str(e), 'error_type': type(e).__name__}
                    )
                    raise
            return wrapper
        return decorator
    @staticmethod
    def get_latest_errors(limit: int = 20):
        """
        Reads the application's log file and returns the last `limit` lines
        that contain "ERROR" or "CRITICAL".
        
        This provides a basic, file-based error monitoring view for the admin dashboard.
        """
        log_file_path = current_app.config.get('LOG_FILE_PATH')
        if not log_file_path or not os.path.exists(log_file_path):
            MonitoringService.log_warning(
                f"Log file not found at path: {log_file_path}. Cannot fetch error logs.",
                "MonitoringService"
            )
            return []

        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            error_logs = []
            # Iterate backwards through the file to find the most recent errors
            for line in reversed(lines):
                if len(error_logs) >= limit:
                    break
                
                # Check for error keywords
                if "ERROR" in line or "CRITICAL" in line:
                    # A simple parser for the default log format:
                    # [YYYY-MM-DD HH:MM:SS,ms] LEVEL: Message [in /path/to/file:line]
                    try:
                        timestamp = line.split(']')[0][1:]
                        level = line.split(']')[1].strip().split(':')[0]
                        message = line.split(':', 2)[-1].strip()
                        
                        error_logs.append({
                            'timestamp': timestamp,
                            'level': level,
                            'message': message
                        })
                    except IndexError:
                        # Fallback for log lines that don't match the expected format
                         error_logs.append({
                            'timestamp': 'N/A',
                            'level': 'UNKNOWN',
                            'message': line.strip()
                        })

            return error_logs

        except Exception as e:
            MonitoringService.log_error(
                f"Failed to read or parse log file: {e}",
                "MonitoringService",
                exc_info=True
            )
            return [] # Return an empty list on failure


