from flask import Blueprint

newsletter_bp = Blueprint('newsletter_bp', __name__)

from . import routes
