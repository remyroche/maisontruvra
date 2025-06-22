from flask import Blueprint
from flask_jwt_extended import JWTManager

auth_bp = Blueprint('auth_bp', __name__)
jwt = JWTManager()

def initialize_jwt(app):
    """Initializes the JWTManager with the Flask app."""
    jwt.init_app(app)

# Import routes to register them with the blueprint
from . import routes
