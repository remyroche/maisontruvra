from flask import Flask
from flask_cors import CORS
from .config import Config
from .database import db, migrate
from .extensions import mail, celery, cache
from .admin_api import admin_api_bp
from .auth import auth_bp
from .b2b import b2b_bp
from .products import products_bp
from .orders import orders_bp
from .cart import cart_bp
from .account import account_bp
from .wishlist import wishlist_bp
from .passport import passport_bp
from .blog import blog_bp
from .newsletter import newsletter_bp
from .inventory import inventory_bp
import os

def create_app(config_class=Config):
    """
    Creates and configures the Flask application.
    """
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    cache.init_app(app)

    # Initialize Celery
    celery.conf.update(app.config)

    # Enable CORS
    CORS(app, supports_credentials=True, resources={
        r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")},
        r"/b2b/*": {"origins": app.config.get("CORS_ORIGINS", "*")},
        r"/admin/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}
    })

    # Register Blueprints
    app.register_blueprint(admin_api_bp, url_prefix='/admin/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(b2b_bp, url_prefix='/api/b2b')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(account_bp, url_prefix='/api/account')
    app.register_blueprint(wishlist_bp, url_prefix='/api/wishlist')
    app.register_blueprint(passport_bp, url_prefix='/api/passport')
    app.register_blueprint(blog_bp, url_prefix='/api/blog')
    app.register_blueprint(newsletter_bp, url_prefix='/api/newsletter')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')

    @app.route('/health')
    def health_check():
        return "OK", 200

    return app