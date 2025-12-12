"""
Production Configuration
========================

Configuration for production environment.

Created: Phase 6 - Configuration System
"""

import os
import logging
from logging.handlers import SysLogHandler
from config.base import BaseConfig, basedir


class ProductionConfig(BaseConfig):
    """Production-specific configuration."""

    # Production mode
    DEBUG = False
    TESTING = False

    # ==========================================
    # Database Configuration
    # ==========================================

    DB_ENGINE = os.getenv('DB_ENGINE')
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASS')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')

    # Build database URI if all required vars are present
    if all([DB_ENGINE, DB_USERNAME, DB_NAME]):
        SQLALCHEMY_DATABASE_URI = (
            f'{DB_ENGINE}://{DB_USERNAME}:{DB_PASSWORD}'
            f'@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        )
    else:
        # Fallback to SQLite
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'db.sqlite3'}"

    # ==========================================
    # Security Settings
    # ==========================================

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True  # Only HTTPS
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_DURATION = 3600

    # ==========================================
    # Logging
    # ==========================================

    LOG_LEVEL = 'WARNING'

    # Debug toolbar
    DEBUG_TB_ENABLED = False

    @staticmethod
    def init_app(app):
        """
        Production-specific initialization.

        Sets up SysLog handler for production logging.

        Args:
            app: Flask application instance
        """
        # Add SysLog handler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)
