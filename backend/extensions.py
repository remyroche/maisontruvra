from argon2 import PasswordHasher
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_redis import FlaskRedis
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
password_hasher = PasswordHasher()
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()
cors = CORS()
cache = Cache()
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address, default_limits=["200 per day", "50 per hour"]
)
redis_client = FlaskRedis()
socketio = SocketIO()
