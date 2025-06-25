from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from flask_mail import Mail
from celery import Celery
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import os
from argon2 import PasswordHasher
from .middleware import setup_middleware, RequestLoggingMiddleware, register_middleware
from .inputsanitizer import InputSanitizer
from backend.logger_and_error_handler import setup_logging, register_error_handlers
from flask_login import user_logged_in, user_login_failed
from flask import request

db = SQLAlchemy()
migrate = Migrate()
ph = PasswordHasher()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
mail = Mail()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})
    mail.init_app(app)
    celery.conf.update(app.config)
    

    # Register CSRF routes
    from backend.auth.csrf_routes import csrf_bp
    app.register_blueprint(csrf_bp, url_prefix='/api/auth')

    # Initialize Celery after the app is configured
    init_celery(app)
    
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
    
    @user_login_failed.connect_via(app)
    def _login_failed(sender, **extra):
        """Log failed login attempts."""
        security_logger.warning({
            'event': 'USER_LOGIN_FAILED',
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'timestamp': datetime.utcnow().isoformat()
        })

    @user_unauthorized.connect_via(app)
    def _login_failed():
        """
        This signal is sent when the LoginManager rejects access for a user.
        It's a good place to catch unauthorized access attempts to @login_required routes.
        """
        security_logger.warning(f"Unauthorized access attempt to a protected endpoint from IP: {request.remote_addr}")


    # Loggin
    app.wsgi_app = RequestLoggingMiddleware(app.wsgi_app)
    setup_logging(app)
    register_error_handlers(app)

    # Register session management middleware
    register_middleware(app)

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

    # Security at middleware level: CSRF, sanitization, HTTPS, ...
    setup_middleware(app)
    init_app_middleware(app)

    @app.before_request
    def make_session_permanent():
        session.permanent = True

    return app
