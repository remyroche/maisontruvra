# This service contains the logic to read and parse the log file.

import os
from flask import current_app

class MonitoringService:
    """
    Service for providing monitoring data, such as reading recent logs
    from the application's log file.
    """
    @staticmethod
    def get_latest_errors(limit: int = 20):
        """
        Reads the application's log file and returns the last `limit` lines
        that contain "ERROR" or "CRITICAL".
        
        This provides a basic, file-based error monitoring view for the admin dashboard.
        """
        log_file_path = current_app.config.get('LOG_FILE_PATH')
        if not log_file_path or not os.path.exists(log_file_path):
            current_app.logger.warning(
                f"Log file not found at path: {log_file_path}. Cannot fetch error logs."
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
            current_app.logger.error(f"Failed to read or parse log file: {e}")
            return [] # Return an empty list on failure



import time
from flask import current_app
from backend.database import db
from backend.services.exceptions import ServiceException
