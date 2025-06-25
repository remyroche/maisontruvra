from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from argon2 import PasswordHasher

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
password_hasher = PasswordHasher()  # Using Argon2 instead of Bcrypt
login_manager = LoginManager()
mail = Mail()
cors = CORS()
limiter = Limiter(key_func=get_remote_address)

