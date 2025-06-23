import os
from flask import Flask
from flask_jwt_extended import JWTManager
from backend.config import Config
from backend.extensions import db, migrate, bcrypt, login_manager, mail, cors, limiter
from flask_wtf.csrf import CSRFProtect

# Import blueprints
from backend.account.routes import account_bp
from backend.admin_api.routes import admin_api_bp
from backend.auth.routes import auth_bp
from backend.b2b.routes import b2b_bp
from backend.blog.routes import blog_bp
from backend.cart.routes import cart_bp
from backend.inventory.routes import inventory_bp
from backend.newsletter.routes import newsletter_bp
from backend.orders.routes import orders_bp
from backend.passport.routes import passport_bp
from backend.products.routes import products_bp
from backend.routes.webhooks import webhooks_bp
from backend.wishlist.routes import wishlist_bp

csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    csrf.init_app(app) # Initialize CSRF protection
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    jwt = JWTManager(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    limiter.init_app(app)

    # Register blueprints
    app.register_blueprint(account_bp, url_prefix='/api/account')
    app.register_blueprint(admin_api_bp, url_prefix='/api/admin')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(b2b_bp, url_prefix='/api/b2b')
    app.register_blueprint(blog_bp, url_prefix='/api/blog')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(newsletter_bp, url_prefix='/api/newsletter')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(passport_bp, url_prefix='/api/passport')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(webhooks_bp, url_prefix='/api/webhooks')
    app.register_blueprint(wishlist_bp, url_prefix='/api/wishlist')

    with app.app_context():
        from backend.models import user_models, product_models, order_models, blog_models, auth_models, b2b_models, b2b_loyalty_models, inventory_models, newsletter_models, passport_models, referral_models, utility_models

    @app.route('/')
    def index():
        return "Welcome to the Maison Truvrain backend!"

    @app.after_request
    def set_csrf_cookie(response):
        from flask_wtf.csrf import generate_csrf
        response.set_cookie('XSRF-TOKEN', generate_csrf())
        return response

    return app
