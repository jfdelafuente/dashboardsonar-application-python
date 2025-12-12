from flask import Flask
from flask_cors import CORS
from .extensions import db, login_manager, migrate, bootstrap, csrf
from .utils.logger import setup_logging
from .errorhandlers import register_error_handlers


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

    # Setup logging first
    setup_logging(app)

    with app.app_context():
        initialize_plugins(app)
        register_blueprints(app)
        register_error_handlers(app)

        # Log application startup
        app.logger.info(f'Application started - Config: {app_config.__name__}')

    return app



