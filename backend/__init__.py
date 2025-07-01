from flask import Flask, request, session, jsonify
from celery import Celery
from flask_talisman import Talisman
from datetime import datetime
import os
from .extensions import db, migrate, cors, jwt
from .celery_worker import celery # Import the celery instance

# Import extension instances from the central extensions file
from .extensions import (
    db,
    migrate,
    login_manager,
    mail,
    limiter,
    redis_client,
    socketio,
    jwt,
    csrf,
    cache,
    cors,
    password_hasher
)

from . import config
from . import services
from .middleware import setup_middleware, check_staff_session, mfa_check_middleware
from .utils.input_sanitizer import init_app_middleware
from .loggers import setup_logging, security_logger
from .logger_and_error_handler import register_error_handlers
from flask_login import user_logged_in, user_unauthorized
from .utils.vite import vite_asset
from .database import setup_database_security

from flask_cors import CORS
from backend.extensions import db, migrate, login_manager
from backend.config import Config
from backend.database import init_db_command
from backend.utils.vite import Vite
import logging


# Configure extensions that need it before app context
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
celery = Celery(__name__, broker=config.Config.CELERY_BROKER_URL)
 
def create_app(config_class=config.Config):
    app = Flask(__name__)
    
    # Handle string configuration names
    if isinstance(config_class, str):
        if config_class == 'default':
            config_class = config.Config
        elif config_class in config.config_by_name:
            config_class = config.config_by_name[config_class]
        else:
            raise ValueError(f"Unknown configuration: {config_class}")
    
    app.config.from_object(config_class)

    # --- Content Security Policy (CSP) ---
    # This policy allows content (scripts, styles, etc.) from the app's own domain
    # and a placeholder for your future CDN. It's a critical security feature.
    csp = {
        'default-src': [
            '\'self\'',
            '*.your-cdn.com'  # Replace with your actual CDN domain
        ],
        'script-src': [
            '\'self\'',
            '\'unsafe-inline\'' # Required for some Vue patterns, can be tightened
        ]
    }
    Talisman(app, content_security_policy=csp)


    # Initialize services
    with app.app_context():
        services.init_app(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    cors.init_app(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})
    mail.init_app(app)
    celery.config_from_object(app.config, namespace='CELERY')
    jwt.init_app(app)
    Vite(app)


    # Setup database security options and logging
    setup_database_security(app)

    # Setup logging
    if not app.debug:
        # In production, you might want to log to a file
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)

    # User loader for Flask-Login
    from backend.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    
    @app.context_processor
    def inject_vite_asset():
        return dict(vite_asset=vite_asset)
        
    # --- Initialize Talisman for security headers ---
    # A restrictive Content-Security-Policy (CSP) is essential for preventing XSS.
    # The default is very strict. The policy below is a starting point.
    # For production, you must carefully craft a policy that fits your application's needs,
    # especially regarding script sources for Vue.js.
    csp = {
        'default-src': '\'self\'',
        'img-src': '*', # Allow images from any source for now
        'script-src': [
            '\'self\'',
            # In production, you would remove 'unsafe-eval' and use a nonce-based approach.
            '\'unsafe-eval\'', 
        ],
        'style-src': [
            '\'self\'',
            # In production, this should be removed.
            '\'unsafe-inline\'',
        ]
    }
    Talisman(app, content_security_policy=csp)

    # Register CSRF routes
    from backend.auth.csrf_routes import csrf_bp
    app.register_blueprint(csrf_bp, url_prefix='/api/auth')

    # Create a custom Celery Task class that ensures every task
    # runs within the Flask application context.
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    
    # --- Signal Handlers for Login Events ---    
    @user_logged_in.connect_via(app)
    def _after_login(sender, user, **extra):
        """Log successful logins."""
        security_logger.info({
            'event': 'USER_LOGIN_SUCCESS',
            'user_id': user.id,
            'email': user.email,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # Note: user_login_failed signal doesn't exist in flask_login
    # Failed login attempts should be logged in the login route itself

    @user_unauthorized.connect_via(app)
    def _login_failed():
        """
        This signal is sent when the LoginManager rejects access for a user.
        It's a good place to catch unauthorized access attempts to @login_required routes.
        """
        security_logger.warning(f"Unauthorized access attempt to a protected endpoint from IP: {request.remote_addr}")


    # Logging
    # app.wsgi_app = RequestLoggingMiddleware(app.wsgi_app)  # RequestLoggingMiddleware class not found
    setup_logging(app)
    register_error_handlers(app)

    # Register session management middleware
    check_staff_session(app)

    # Import and register blueprints
    from .routes.webhooks import webhooks_bp
    app.register_blueprint(webhooks_bp, url_prefix='/api/webhooks')

    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from .account.routes import account_bp
    app.register_blueprint(account_bp, url_prefix='/api/account')

    from .products.routes import products_bp
    app.register_blueprint(products_bp, url_prefix='/api/products')
    
    from .products.review_routes import reviews_bp
    app.register_blueprint(reviews_bp, url_prefix='/api/reviews')

    from .cart.routes import cart_bp
    app.register_blueprint(cart_bp, url_prefix='/api/cart')

    from .orders.routes import orders_bp
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    
    from .wishlist.routes import wishlist_bp
    app.register_blueprint(wishlist_bp, url_prefix='/api/wishlist')

    from .newsletter.routes import newsletter_bp
    app.register_blueprint(newsletter_bp, url_prefix='/api/newsletter')

    from .blog.routes import blog_bp
    app.register_blueprint(blog_bp, url_prefix='/api/blog')

    from .passport.routes import passport_bp
    app.register_blueprint(passport_bp, url_prefix='/api/passport')
    
    # B2B Blueprints
    from .b2b.auth_routes import b2b_auth_bp
    app.register_blueprint(b2b_auth_bp, url_prefix='/api/b2b/auth')

    from .b2b.dashboard_routes import b2b_dashboard_bp
    app.register_blueprint(b2b_dashboard_bp, url_prefix='/api/b2b/dashboard')

    from .b2b.product_routes import b2b_product_bp
    app.register_blueprint(b2b_product_bp, url_prefix='/api/b2b/products')
    
    from .b2b.order_routes import b2b_order_bp
    app.register_blueprint(b2b_order_bp, url_prefix='/api/b2b/orders')

    from .b2b.profile_routes import b2b_profile_bp
    app.register_blueprint(b2b_profile_bp, url_prefix='/api/b2b/profile')

    from backend.api.b2b_routes import b2b_bp # New B2B routes
    app.register_blueprint(b2b_bp)

    from backend.api.referral_routes import referral_bp # New Referral routes
    app.register_blueprint(referral_bp)

    from .b2b.invoice_routes import b2b_invoice_bp
    app.register_blueprint(b2b_invoice_bp, url_prefix='/api/b2b/invoices')
    
    from .b2b.loyalty_routes import b2b_loyalty_bp
    app.register_blueprint(b2b_loyalty_bp, url_prefix='/api/b2b/loyalty')

    from .b2b.referral_routes import b2b_referral_bp
    app.register_blueprint(b2b_referral_bp, url_prefix='/api/b2b/referrals')

    from .b2b.b2b_quick_order import b2b_quick_order_bp
    app.register_blueprint(b2b_quick_order_bp, url_prefix='/api/b2b/quick-order')

    from .main_routes import main_bp
    app.register_blueprint(main_bp)

    # Admin API Blueprints
    from .admin_api.auth_routes import admin_auth_bp
    app.register_blueprint(admin_auth_bp, url_prefix='/api/admin/auth')
    
    from .admin_api.dashboard_routes import admin_dashboard_bp
    app.register_blueprint(admin_dashboard_bp, url_prefix='/api/admin/dashboard')

    from .admin_api.user_management_routes import admin_user_management_bp
    app.register_blueprint(admin_user_management_bp, url_prefix='/api/admin/users')

    from .admin_api.product_management_routes import admin_product_management_bp
    app.register_blueprint(admin_product_management_bp, url_prefix='/api/admin/products')

    from .admin_api.order_routes import admin_order_bp
    app.register_blueprint(admin_order_bp, url_prefix='/api/admin/orders')

    from .admin_api.review_routes import admin_review_bp
    app.register_blueprint(admin_review_bp, url_prefix='/api/admin/reviews')
    
    from .admin_api.site_management_routes import admin_site_management_bp
    app.register_blueprint(admin_site_management_bp, url_prefix='/api/admin/site')

    from .admin_api.audit_log_routes import admin_audit_log_bp
    app.register_blueprint(admin_audit_log_bp, url_prefix='/api/admin/audit-log')

    from .admin_api.monitoring_routes import admin_monitoring_bp
    app.register_blueprint(admin_monitoring_bp, url_prefix='/api/admin/monitoring')
    
    from .admin_api.newsletter_routes import admin_newsletter_bp
    app.register_blueprint(admin_newsletter_bp, url_prefix='/api/admin/newsletter')
    
    from .admin_api.loyalty_routes import admin_loyalty_bp
    app.register_blueprint(admin_loyalty_bp, url_prefix='/api/admin/loyalty')

    from .admin_api.b2b_management_routes import admin_b2b_management_bp
    app.register_blueprint(admin_b2b_management_bp, url_prefix='/api/admin/b2b')
    
    from .admin_api.pos_routes import admin_pos_bp
    app.register_blueprint(admin_pos_bp, url_prefix='/api/admin/pos')
    
    from .admin_api.delivery_routes import admin_delivery_bp
    app.register_blueprint(admin_delivery_bp, url_prefix='/api/admin/delivery')

    from .admin_api.quote_routes import admin_quote_bp
    app.register_blueprint(admin_quote_bp, url_prefix='/api/admin/quotes')
    
    from .admin_api.blog_routes import admin_blog_bp
    app.register_blueprint(admin_blog_bp, url_prefix='/api/admin/blog')
    
    from .admin_api.passport_routes import admin_passport_bp
    app.register_blueprint(admin_passport_bp, url_prefix='/api/admin/passports')

    from .admin_api.session_routes import admin_session_bp
    app.register_blueprint(admin_session_bp, url_prefix='/api/admin/sessions')

    from .contact.routes import contact_bp
    app.register_blueprint(contact_bp)

    # Caching
    cache.init_app(app)
    limiter.init_app(app)
    redis_client.init_app(app)
    socketio.init_app(app, async_mode='eventlet')

    # Add a command to initialize the database
    app.cli.add_command(init_db_command)

    # === JWT Blocklist Implementation ===
    # This callback checks if a JWT has been revoked.
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

    return app
