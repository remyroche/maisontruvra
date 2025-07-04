# ruff: noqa: F401, E402
from flask import Blueprint

admin_api_blueprint = Blueprint("admin_api", __name__, url_prefix="/api/admin")

# Import routes to register them with the blueprint
# The noqa comments disable warnings for unused imports and imports not at the top,
# which are necessary here for Flask's blueprint registration to work correctly.
from . import (
    asset_routes,
    audit_log_routes,
    auth_routes,
    b2b_management_routes,
    blog_management_routes,
    category_management_routes,
    collection_management_routes,
    dashboard_routes,
    delivery_routes,
    discount_management_routes,
    inventory_management_routes,
    invoice_routes,
    loyalty_routes,
    monitoring_routes,
    newsletter_routes,
    order_routes,
    passport_routes,
    pos_routes,
    product_management_routes,
    recommendation_routes,
    recycling_bin_routes,
    review_routes,
    session_routes,
    site_management_routes,
    user_management_routes,
)
