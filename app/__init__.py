import logging
import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.routes import monthly
from config import Config


db = SQLAlchemy()
# Initialize Flask-Bcrypt
bcrypt = Bcrypt()
# Initialize Flask-Login
login_manager = LoginManager()
# Configure the login view
login_manager.login_view = 'auth.login'
# Initialize Flask-Migrate
migrate = Migrate()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True, template_folder='templates', static_folder='static')
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    app.template_folder = 'templates'
    # Register the blueprints
    from app.routes.main import main
    from app.routes.auth import auth
    from app.routes.daily import daily
    from app.routes.monthly import monthly
    from app.routes.settings import settings

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(daily, url_prefix='/daily')
    app.register_blueprint(monthly, url_prefix='/monthly')
    app.register_blueprint(settings, url_prefix='/settings')

    from app import models
    from app import forms

    return app

# Load the user loader function for Flask-Login
from app.models import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))