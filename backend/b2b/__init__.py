from flask import Blueprint

b2b_bp = Blueprint("b2b_bp", __name__)

# Import routes to register them with the blueprint
from . import (
    auth_routes,
    dashboard_routes,
    invoice_routes,
    loyalty_routes,
    order_routes,
    product_routes,
    profile_routes,
    referral_routes,
)
