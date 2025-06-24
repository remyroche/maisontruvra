from flask import Blueprint, render_template
from flask_wtf.csrf import generate_csrf

main_bp = Blueprint('main', __name__)

@main_bp.route('/', defaults={'path': ''})
@main_bp.route('/<path:path>')
def catch_all(path):
    """
    This catch-all route serves the main index.html file for any non-API request.
    It now also generates and injects a CSRF token into the template.
    This allows Vue Router to handle the routing on the client side while ensuring
    the frontend always has a valid token for API calls.
    """
    csrf_token = generate_csrf()
    return render_template("index.html", csrf_token=csrf_token)
