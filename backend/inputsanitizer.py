# backend/inputsanitizer.py

"""
This module is deprecated. Please use backend.utils.input_sanitizer instead.
This file is kept for backward compatibility but will be removed in a future version.
"""

from backend.utils.input_sanitizer import (
    InputSanitizer,
    sanitize_json_request_data,
    sanitize_form_request_data,
    sanitize_url_params,
    init_app_middleware
)

# Import for backward compatibility
from flask import Flask
