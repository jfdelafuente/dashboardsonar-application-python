from flask import Flask
from flask_cors import CORS
from .extensions import db, login_manager, migrate, bootstrap, csrf
from .utils.logger import setup_logging
from .errorhandlers import register_error_handlers


def register_blueprints(app: Flask) -> None:
    """
    Register all application blueprints.

    Args:
        app: Flask application instance

    Blueprints registered:
        - accounts_bp: User authentication and management
        - home_bp: Main dashboard views
        - charts_bp: Data visualization endpoints (prefix: /charts)
        - api_bp: RESTful API endpoints
    """
    from infocodest.accounts.views import accounts_bp
    from infocodest.home.views import home_bp
    from infocodest.charts.views import charts_bp
    from infocodest.api.views import api_bp

    # Register blueprints
    app.register_blueprint(accounts_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(charts_bp, url_prefix='/charts')
    app.register_blueprint(api_bp)

    app.logger.debug('All blueprints registered successfully')


def initialize_extensions(app: Flask) -> None:
    """
    Initialize Flask extensions.

    Args:
        app: Flask application instance

    Extensions initialized:
        - login_manager: Flask-Login for session management
        - db: SQLAlchemy database
        - migrate: Flask-Migrate for database migrations
        - bootstrap: Flask-Bootstrap for UI components
        - csrf: CSRF protection
        - CORS: Cross-Origin Resource Sharing
    """
    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    csrf.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

    app.logger.debug('All extensions initialized successfully')


def create_app(app_config) -> Flask:
    """
    Application factory pattern.

    Creates and configures the Flask application with all necessary
    extensions, blueprints, and error handlers.

    Args:
        app_config: Configuration class (Development, Production, Testing)

    Returns:
        Configured Flask application instance

    Initialization order:
        1. Load configuration
        2. Setup structured logging
        3. Initialize extensions
        4. Register blueprints
        5. Register error handlers
        6. Log startup information
    """
    app = Flask(__name__)
    app.config.from_object(app_config)

    # Setup logging first
    setup_logging(app)

    with app.app_context():
        # Initialize extensions
        initialize_extensions(app)

        # Register blueprints
        register_blueprints(app)

        # Register error handlers
        register_error_handlers(app)

        # Log application startup
        app.logger.info(f'Application started - Config: {app_config.__name__}')

    return app



