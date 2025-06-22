from flask import Blueprint

# This blueprint will serve the admin-specific API endpoints.
admin_api_bp = Blueprint('admin_api_bp', __name__)

# Import routes to register them with the blueprint
from . import user_management_routes, product_management_routes, order_routes, dashboard_routes, site_management_routes, auth_routes, audit_log_routes, b2b_management_routes, blog_routes, loyalty_routes, monitoring_routes, newsletter_routes, passport_routes, pos_routes, quote_routes, review_routes, session_routes
