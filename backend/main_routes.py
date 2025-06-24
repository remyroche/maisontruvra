from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/', defaults={'path': ''})
@main_bp.route('/<path:path>')
def catch_all(path):
    """
    This catch-all route serves the main index.html file for any non-API request.
    This allows Vue Router to handle the routing on the client side.
    """
    return render_template("index.html")

