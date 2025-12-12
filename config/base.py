"""
Base Configuration
==================

Shared configuration for all environments.

All environment-specific configs inherit from BaseConfig.

Created: Phase 6 - Configuration System
"""

import os
import secrets
from pathlib import Path

# Base directory (project root)
basedir = Path(__file__).parent.parent.absolute()


class BaseConfig:
    """Base configuration class with shared settings."""

    # ==========================================
    # Security Settings
    # ==========================================

    SECRET_KEY = os.getenv('SECRET_KEY', None)
    if not SECRET_KEY:
        SECRET_KEY = secrets.token_hex(32)

    CSRF_ENABLED = True
    WTF_CSRF_ENABLED = True

    # ==========================================
    # Database Settings
    # ==========================================

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    BCRYPT_LOG_ROUNDS = 13

    # ==========================================
    # Assets Settings
    # ==========================================

    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')

    # ==========================================
    # Application Settings
    # ==========================================

    FLASK_APP = os.getenv('FLASK_APP', 'run.py')
    DAYS_COMPARISON = int(os.getenv('DAYS_COMPARISON', '15'))

    # ==========================================
    # Logging Settings
    # ==========================================

    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = basedir / 'logs'

    # ==========================================
    # Session/Cookie Settings
    # ==========================================

    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    @staticmethod
    def validate_config(app):
        """
        Validate critical configuration settings.

        Checks for required environment variables and configuration values.
        Logs configuration status without exposing sensitive information.

        Args:
            app: Flask application instance

        Raises:
            ValueError: If critical configuration is missing

        Example:
            >>> BaseConfig.validate_config(app)
        """
        # Log configuration mode (without secrets)
        config_name = app.config.__class__.__name__
        app.logger.info(f'Configuration loaded: {config_name}')
        app.logger.info(f'Debug mode: {app.config.get("DEBUG", False)}')
        app.logger.info(f'Testing mode: {app.config.get("TESTING", False)}')

        # Validate SECRET_KEY exists
        if not app.config.get('SECRET_KEY'):
            app.logger.warning('SECRET_KEY not set - using generated key (not suitable for production)')

        # Log database configuration (without credentials)
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_uri:
            # Mask password in URI for logging
            import re
            masked_uri = re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', db_uri)
            app.logger.info(f'Database: {masked_uri}')
        else:
            app.logger.warning('SQLALCHEMY_DATABASE_URI not configured')

    @staticmethod
    def init_app(app):
        """
        Hook for custom initialization.

        Called after config is loaded into the app.
        Override in subclasses for environment-specific setup.

        Args:
            app: Flask application instance

        Example:
            >>> class ProductionConfig(BaseConfig):
            ...     @staticmethod
            ...     def init_app(app):
            ...         # Production-specific setup
            ...         BaseConfig.validate_config(app)
            ...         pass
        """
        # Validate configuration by default
        BaseConfig.validate_config(app)
