#!/usr/bin/env python3
"""
Example file to demonstrate HTTPS security checks
"""

import requests
import urllib3

# This will be flagged as insecure HTTP URL
API_URL = "http://api.example.com/v1"

# This will be flagged as SSL verification disabled
def make_insecure_request():
    response = requests.get("https://api.example.com", verify=False)
    return response.json()

# This will be flagged as disabling SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# This is good - HTTPS URL
SECURE_API_URL = "https://api.example.com/v1"

# This is good - proper request with SSL verification
def make_secure_request():
    response = requests.get(SECURE_API_URL)
    return response.json()

# Flask app example without HTTPS enforcement
from flask import Flask

app = Flask(__name__)

@app.route('/api/data')
def get_data():
    return {"message": "Hello World"}

if __name__ == '__main__':
    # This will be flagged - no HTTPS enforcement
    app.run(debug=True)  # This will also be flagged for debug mode