from flask import Flask
from .errorhandlers import error_401, error_404, error_500
from flask_cors import CORS
from .extensions import db, login_manager, migrate, bootstrap, csrf

def register_error_handlers(app):
    # Registering Errorhandler
    app.register_error_handler(401, error_401)
    app.register_error_handler(404, error_404)
    app.register_error_handler(500, error_500)


def register_blueprints(app):
    from infocodest.accounts.views import accounts_bp
    from infocodest.home.views import home_bp
    from infocodest.charts.views import charts_bp
    from infocodest.api.views import api_bp
    
    # Registering blueprints
    app.register_blueprint(accounts_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(charts_bp, url_prefix='/charts')
    app.register_blueprint(api_bp)


def initialize_plugins(app):
    # Initialize Plugins
    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    csrf.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}})


def create_app(app_config):
    """Initialize the core application."""
    app = Flask(__name__)
    app.config.from_object(app_config)
    with app.app_context():
        initialize_plugins(app)
        register_blueprints(app)
        register_error_handlers(app)
    return app



