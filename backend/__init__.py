import logging
from datetime import datetime

from celery import Celery
from flask import Flask, request, session
from flask_login import user_logged_in, user_unauthorized
from flask_talisman import Talisman

from . import config, services
from .celery_worker import init_celery
from .database import init_db_command, setup_database_security

# Import extension instances from the central extensions file
from .extensions import (
    cache,
    cors,
    csrf,
    db,
    jwt,
    limiter,
    login_manager,
    mail,
    migrate,
    redis_client,
    socketio,
)
from .logger_and_error_handler import register_error_handlers
from .loggers import api_logger, database_logger, security_logger, setup_logging
from .utils.vite import Vite
from .middleware import check_staff_session, mfa_check_middleware, setup_middleware
from .utils.input_sanitizer import init_app_middleware
from .utils.vite import vite_asset

# Configure extensions that need it before app context
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"
celery = Celery(__name__, broker=config.Config.CELERY_BROKER_URL)


def _configure_app(app: Flask, config_class) -> None:
    """Configure the Flask app with the given configuration class."""
    # Handle string configuration names
    if isinstance(config_class, str):
        if config_class == "default":
            config_class = config.Config
        elif config_class in config.config_by_name:
            config_class = config.config_by_name[config_class]
        else:
            raise ValueError(f"Unknown configuration: {config_class}")

    app.config.from_object(config_class)


def _setup_security_headers(app: Flask) -> None:
    """Setup security headers and CSP."""
    # --- Content Security Policy (CSP) ---
    # This policy allows content (scripts, styles, etc.) from the app's own domain
    # and a placeholder for your future CDN. It's a critical security feature.
    csp = {
        "default-src": [
            "'self'",
            "*.your-cdn.com",  # Replace with your actual CDN domain
        ],
        "script-src": [
            "'self'",
            "'unsafe-inline'",  # Required for some Vue patterns, can be tightened
        ],
    }
    Talisman(app, content_security_policy=csp)


def _setup_extensions(app: Flask) -> None:
    """Initialize Flask extensions."""
    # Initialize services
    with app.app_context():
        services.init_app(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    # Get allowed origins from environment variable or use default
    allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
    cors.init_app(
        app, 
        supports_credentials=True, 
        resources={r"/api/*": {"origins": allowed_origins}}
    )
    mail.init_app(app)
    celery.config_from_object(app.config, namespace="CELERY")
    jwt.init_app(app)
    Vite(app)
    init_celery(app)

    # Setup database security options and logging
    setup_database_security(app)

    # Setup logging
    if not app.debug:
        # In production, you might want to log to a file
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)


def _setup_blueprints(app: Flask) -> None:
    """Register all application blueprints."""
    # Register CSRF routes
    from backend.auth.csrf_routes import csrf_bp
    app.register_blueprint(csrf_bp, url_prefix="/api/auth")

    # Register unified auth routes (replaces separate B2B/B2C auth)
    from backend.auth.unified_routes import unified_auth_bp
    app.register_blueprint(unified_auth_bp)

    # Keep legacy auth routes for backward compatibility
    from backend.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth/legacy")

    # Register all other blueprints
    _register_core_blueprints(app)
    _register_b2b_blueprints(app)
    _register_admin_blueprints(app)


def _register_core_blueprints(app: Flask) -> None:
    """Register core application blueprints."""
    from .routes.webhooks import webhooks_bp
    from .account.routes import account_bp
    from .products.routes import products_bp
    from .products.review_routes import reviews_bp
    from .cart.routes import cart_bp
    from .orders.routes import orders_bp
    from .wishlist.routes import wishlist_bp
    from .newsletter.routes import newsletter_bp
    from .blog.routes import blog_bp
    from .passport.routes import passport_bp
    from .main_routes import main_bp
    from .contact.routes import contact_bp

    app.register_blueprint(webhooks_bp, url_prefix="/api/webhooks")
    app.register_blueprint(account_bp, url_prefix="/api/account")
    app.register_blueprint(products_bp, url_prefix="/api/products")
    app.register_blueprint(reviews_bp, url_prefix="/api/reviews")
    app.register_blueprint(cart_bp, url_prefix="/api/cart")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")
    app.register_blueprint(wishlist_bp, url_prefix="/api/wishlist")
    app.register_blueprint(newsletter_bp, url_prefix="/api/newsletter")
    app.register_blueprint(blog_bp, url_prefix="/api/blog")
    app.register_blueprint(passport_bp, url_prefix="/api/passport")
    app.register_blueprint(main_bp)
    app.register_blueprint(contact_bp)


def _register_b2b_blueprints(app: Flask) -> None:
    """Register B2B specific blueprints."""
    from .b2b.auth_routes import b2b_auth_bp
    from .b2b.dashboard_routes import b2b_dashboard_bp
    from .b2b.product_routes import b2b_product_bp
    from .b2b.order_routes import b2b_order_bp
    from .b2b.profile_routes import b2b_profile_bp
    from .b2b.invoice_routes import b2b_invoice_bp
    from .b2b.loyalty_routes import b2b_loyalty_bp
    from .b2b.referral_routes import b2b_referral_bp
    from .b2b.b2b_quick_order import b2b_quick_order_bp
    from backend.api.b2b_routes import b2b_bp
    from backend.api.referral_routes import referral_bp

    app.register_blueprint(b2b_auth_bp, url_prefix="/api/b2b/auth")
    app.register_blueprint(b2b_dashboard_bp, url_prefix="/api/b2b/dashboard")
    app.register_blueprint(b2b_product_bp, url_prefix="/api/b2b/products")
    app.register_blueprint(b2b_order_bp, url_prefix="/api/b2b/orders")
    app.register_blueprint(b2b_profile_bp, url_prefix="/api/b2b/profile")
    app.register_blueprint(b2b_invoice_bp, url_prefix="/api/b2b/invoices")
    app.register_blueprint(b2b_loyalty_bp, url_prefix="/api/b2b/loyalty")
    app.register_blueprint(b2b_referral_bp, url_prefix="/api/b2b/referrals")
    app.register_blueprint(b2b_quick_order_bp, url_prefix="/api/b2b/quick-order")
    app.register_blueprint(b2b_bp)
    app.register_blueprint(referral_bp)


def _register_admin_blueprints(app: Flask) -> None:
    """Register admin API blueprints."""
    from .admin_api.auth_routes import admin_auth_bp
    from .admin_api.dashboard_routes import admin_dashboard_bp
    from .admin_api.user_management_routes import admin_user_management_bp
    from .admin_api.product_management_routes import admin_product_management_bp
    from .admin_api.order_routes import admin_order_bp
    from .admin_api.review_routes import admin_review_bp
    from .admin_api.site_management_routes import admin_site_management_bp
    from .admin_api.audit_log_routes import admin_audit_log_bp
    from .admin_api.monitoring_routes import admin_monitoring_bp
    from .admin_api.newsletter_routes import admin_newsletter_bp
    from .admin_api.loyalty_routes import admin_loyalty_bp
    from .admin_api.b2b_management_routes import admin_b2b_management_bp
    from .admin_api.pos_routes import admin_pos_bp
    from .admin_api.delivery_routes import admin_delivery_bp
    from .admin_api.blog_management_routes import bp as admin_blog_bp
    from .admin_api.passport_routes import admin_passport_bp
    from .admin_api.session_routes import admin_session_bp
    from .admin_api.recommendation_routes import admin_recommendation_bp
    from backend.admin_api.recycling_bin_routes import recycling_bin_bp

    app.register_blueprint(admin_auth_bp, url_prefix="/api/admin/auth")
    app.register_blueprint(admin_dashboard_bp, url_prefix="/api/admin/dashboard")
    app.register_blueprint(admin_user_management_bp, url_prefix="/api/admin/users")
    app.register_blueprint(admin_product_management_bp, url_prefix="/api/admin/products")
    app.register_blueprint(admin_order_bp, url_prefix="/api/admin/orders")
    app.register_blueprint(admin_review_bp, url_prefix="/api/admin/reviews")
    app.register_blueprint(admin_site_management_bp, url_prefix="/api/admin/site")
    app.register_blueprint(admin_audit_log_bp, url_prefix="/api/admin/audit-log")
    app.register_blueprint(admin_monitoring_bp, url_prefix="/api/admin/monitoring")
    app.register_blueprint(admin_newsletter_bp, url_prefix="/api/admin/newsletter")
    app.register_blueprint(admin_loyalty_bp, url_prefix="/api/admin/loyalty")
    app.register_blueprint(admin_b2b_management_bp, url_prefix="/api/admin/b2b")
    app.register_blueprint(admin_pos_bp, url_prefix="/api/admin/pos")
    app.register_blueprint(admin_delivery_bp, url_prefix="/api/admin/delivery")
    app.register_blueprint(admin_blog_bp)
    app.register_blueprint(admin_passport_bp, url_prefix="/api/admin/passports")
    app.register_blueprint(admin_session_bp, url_prefix="/api/admin/sessions")
    app.register_blueprint(admin_recommendation_bp)
    app.register_blueprint(recycling_bin_bp)


def create_app(config_class=config.Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Configure the app
    _configure_app(app, config_class)
    _setup_security_headers(app)
    _setup_extensions(app)

    # Setup user loader and context processors
    _setup_user_loader(app)
    _setup_context_processors(app)
    
    # Setup additional security headers
    _setup_additional_security(app)
    
    # Setup Celery context
    _setup_celery_context(app)
    
    # Setup signal handlers
    _setup_signal_handlers(app)
    
    # Setup logging and error handling
    setup_logging(app)
    register_error_handlers(app)
    
    # Register all blueprints
    _setup_blueprints(app)
    
    # Setup additional middleware and final configuration
    _setup_final_configuration(app)

    return app


def _setup_user_loader(app: Flask) -> None:
    """Setup Flask-Login user loader."""
    from backend.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


def _setup_context_processors(app: Flask) -> None:
    """Setup template context processors."""
    @app.context_processor
    def inject_vite_asset():
        return {"vite_asset": vite_asset}


def _setup_additional_security(app: Flask) -> None:
    """Setup additional security headers."""
    # A restrictive Content-Security-Policy (CSP) is essential for preventing XSS.
    csp = {
        "default-src": "'self'",
        "img-src": "*",  # Allow images from any source for now
        "script-src": [
            "'self'",
            # In production, you would remove 'unsafe-eval' and use a nonce-based approach.
            "'unsafe-eval'",
        ],
        "style-src": [
            "'self'",
            # In production, this should be removed.
            "'unsafe-inline'",
        ],
    }
    Talisman(app, content_security_policy=csp)


def _setup_celery_context(app: Flask) -> None:
    """Setup Celery context for background tasks."""
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask


def _setup_signal_handlers(app: Flask) -> None:
    """Setup Flask signal handlers for logging."""
    @user_logged_in.connect_via(app)
    def _after_login(sender, user, **extra):
        """Log successful logins."""
        security_logger.info(
            {
                "event": "USER_LOGIN_SUCCESS",
                "user_id": user.id,
                "email": user.email,
                "ip_address": request.remote_addr,
                "user_agent": request.headers.get("User-Agent"),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    @user_unauthorized.connect_via(app)
    def _login_failed():
        """Log unauthorized access attempts."""
        security_logger.warning(
            f"Unauthorized access attempt to a protected endpoint from IP: {request.remote_addr}"
        )


def _setup_final_configuration(app: Flask) -> None:
    """Setup final application configuration."""
    # Register session management middleware
    check_staff_session(app)

    # Caching
    cache.init_app(app)
    limiter.init_app(app)
    redis_client.init_app(app)
    socketio.init_app(app, async_mode="eventlet")

    # Add a command to initialize the database
    app.cli.add_command(init_db_command)

    # JWT Blocklist Implementation
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        # Checks if the jti (JWT ID) exists in the Redis blocklist set
        token_is_revoked = redis_client.get(jti)
        return token_is_revoked is not None

    # Security at middleware level: CSRF, sanitization, HTTPS, ...
    setup_middleware(app)
    mfa_check_middleware(app)
    init_app_middleware(app)  # Initialize input sanitization middleware

    @app.before_request
    def make_session_permanent():
        session.permanent = True
