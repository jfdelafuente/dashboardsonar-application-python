"""
Production Configuration
========================

Configuration for production environment.

Created: Phase 6 - Configuration System
Updated: Phase 1 Improvements - Added SECRET_KEY validation and URI escaping
Updated: Phase 3 Improvements - Add comprehensive type hints
"""

from __future__ import annotations

import os
import logging
from logging.handlers import SysLogHandler
from typing import ClassVar, Optional
from config.base import BaseConfig, basedir
from config.utils import build_database_uri


class ProductionConfig(BaseConfig):
    """Production-specific configuration."""

    # Production mode
    DEBUG: ClassVar[bool] = False
    TESTING: ClassVar[bool] = False

    # ==========================================
    # Security - SECRET_KEY (validated in init_app)
    # ==========================================

    SECRET_KEY: ClassVar[Optional[str]] = os.getenv('SECRET_KEY')

    # If not set, will be validated in init_app() when actually used
    # This allows importing the config module without failing

    # ==========================================
    # Database Configuration
    # ==========================================

    DB_ENGINE: ClassVar[Optional[str]] = os.getenv('DB_ENGINE')
    DB_USERNAME: ClassVar[Optional[str]] = os.getenv('DB_USERNAME')
    DB_PASSWORD: ClassVar[Optional[str]] = os.getenv('DB_PASS')
    DB_HOST: ClassVar[Optional[str]] = os.getenv('DB_HOST')
    DB_PORT: ClassVar[Optional[str]] = os.getenv('DB_PORT')
    DB_NAME: ClassVar[Optional[str]] = os.getenv('DB_NAME')

    # Build database URI using centralized function
    if all([DB_ENGINE, DB_USERNAME, DB_NAME]):
        try:
            SQLALCHEMY_DATABASE_URI = build_database_uri(
                engine=DB_ENGINE,
                username=DB_USERNAME,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=int(DB_PORT) if DB_PORT else None,
                database=DB_NAME
            )
        except ValueError as e:
            raise ValueError(f"Database configuration error: {e}")
    else:
        # Fallback to SQLite (warning will be shown in init_app if this config is used)
        SQLALCHEMY_DATABASE_URI = build_database_uri(
            engine='sqlite',
            sqlite_path=basedir / 'db.sqlite3'
        )

    # ==========================================
    # Security Settings
    # ==========================================

    SESSION_COOKIE_HTTPONLY: ClassVar[bool] = True
    SESSION_COOKIE_SECURE: ClassVar[bool] = True  # Only HTTPS
    REMEMBER_COOKIE_HTTPONLY: ClassVar[bool] = True
    REMEMBER_COOKIE_SECURE: ClassVar[bool] = True
    REMEMBER_COOKIE_DURATION: ClassVar[int] = 3600

    # ==========================================
    # Logging
    # ==========================================

    LOG_LEVEL: ClassVar[str] = 'WARNING'

    # Debug toolbar
    DEBUG_TB_ENABLED: ClassVar[bool] = False

    @staticmethod
    def init_app(app: 'Flask') -> None:
        """
        Production-specific initialization.

        Validates SECRET_KEY and sets up SysLog handler for production logging.

        Args:
            app: Flask application instance

        Raises:
            ValueError: If SECRET_KEY is missing, too short, or set to default value
        """
        # Validate SECRET_KEY in production
        secret_key = app.config.get('SECRET_KEY')

        # Validate SECRET_KEY is set
        if not secret_key:
            raise ValueError(
                "SECRET_KEY environment variable is required in production.\n"
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )

        # Validate SECRET_KEY is not the default value
        if secret_key == 'your-secret-key-here-change-in-production':
            raise ValueError(
                "SECRET_KEY is still set to the default value.\n"
                "Generate a new one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )

        # Validate SECRET_KEY has minimum length
        if len(secret_key) < 32:
            raise ValueError(
                f"SECRET_KEY must be at least 32 characters (current: {len(secret_key)}).\n"
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )

        app.logger.info("SECRET_KEY validation passed")

        # Check if using SQLite fallback due to missing database variables
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if 'sqlite' in db_uri.lower():
            if not all([
                ProductionConfig.DB_ENGINE,
                ProductionConfig.DB_USERNAME,
                ProductionConfig.DB_NAME
            ]):
                app.logger.warning(
                    "Missing database environment variables. "
                    "Required: DB_ENGINE, DB_USERNAME, DB_NAME. "
                    "Falling back to SQLite."
                )

        # Add SysLog handler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)
