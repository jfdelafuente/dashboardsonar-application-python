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
        2. Validate configuration (via init_app)
        3. Setup structured logging
        4. Initialize extensions
        5. Register blueprints
        6. Register error handlers
        7. Add health check endpoint
        8. Log startup information
    """
    app = Flask(__name__)
    app.config.from_object(app_config)

    # Validate configuration (calls validate_config internally)
    app_config.init_app(app)

    # Setup logging first
    setup_logging(app)

    with app.app_context():
        # Initialize extensions
        initialize_extensions(app)

        # Register blueprints
        register_blueprints(app)

        # Register error handlers
        register_error_handlers(app)

        # Add health check endpoint for Docker
        @app.route('/health')
        def health_check():
            """Health check endpoint for Docker and monitoring."""
            from flask import jsonify
            try:
                # Check database connectivity
                db.session.execute(db.text('SELECT 1'))
                return jsonify({'status': 'healthy', 'database': 'connected'}), 200
            except Exception as e:
                app.logger.error(f'Health check failed: {str(e)}')
                return jsonify({'status': 'unhealthy', 'error': str(e)}), 503

        # Log application startup
        app.logger.info(f'Application started - Config: {app_config.__name__}')

    return app



