"""
Base Configuration
==================

Shared configuration for all environments.

All environment-specific configs inherit from BaseConfig.

Created: Phase 6 - Configuration System
Updated: Phase 1 Improvements - Use shared mask_db_uri utility
Updated: Phase 2 Improvements - Use str_to_bool, validate ASSETS_ROOT
Updated: Phase 3 Improvements - Add comprehensive type hints
"""

from __future__ import annotations

import os
import secrets
import logging
from pathlib import Path
from typing import ClassVar, Optional

from .utils import mask_db_uri, str_to_bool

# Base directory (project root)
basedir: Path = Path(__file__).parent.parent.absolute()


class BaseConfig:
    """Base configuration class with shared settings."""

    # ==========================================
    # Security Settings
    # ==========================================

    SECRET_KEY: ClassVar[str] = os.getenv('SECRET_KEY', None) or secrets.token_hex(32)
    CSRF_ENABLED: ClassVar[bool] = True
    WTF_CSRF_ENABLED: ClassVar[bool] = True

    # ==========================================
    # Database Settings
    # ==========================================

    SQLALCHEMY_TRACK_MODIFICATIONS: ClassVar[bool] = str_to_bool(
        os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS'),
        default=False
    )
    SQLALCHEMY_ECHO: ClassVar[bool] = False
    BCRYPT_LOG_ROUNDS: ClassVar[int] = 13

    # ==========================================
    # Assets Settings
    # ==========================================

    ASSETS_ROOT: ClassVar[str] = os.getenv('ASSETS_ROOT', '/static/assets')

    # ==========================================
    # Application Settings
    # ==========================================

    FLASK_APP: ClassVar[str] = os.getenv('FLASK_APP', 'run.py')
    DAYS_COMPARISON: ClassVar[int] = int(os.getenv('DAYS_COMPARISON', '15'))

    # ==========================================
    # Logging Settings
    # ==========================================

    LOG_LEVEL: ClassVar[str] = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR: ClassVar[Path] = basedir / 'logs'

    # ==========================================
    # Session/Cookie Settings
    # ==========================================

    SESSION_COOKIE_HTTPONLY: ClassVar[bool] = True
    REMEMBER_COOKIE_HTTPONLY: ClassVar[bool] = True
    REMEMBER_COOKIE_DURATION: ClassVar[int] = 3600

    # ==========================================
    # Data Files Settings
    # ==========================================

    DATA_DIR: ClassVar[str] = os.getenv('DATA_DIR', './datos')
    METRICAS_FILENAME: ClassVar[str] = os.getenv('METRICAS_FILENAME', 'metricas.csv')
    HISTORICO_FILENAME: ClassVar[str] = os.getenv('HISTORICO_FILENAME', 'historico.csv')
    PROVEEDORES_FILENAME: ClassVar[str] = os.getenv('PROVEEDORES_FILENAME', 'proveedores.csv')

    @staticmethod
    def validate_config(app: 'Flask') -> None:
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
            # Mask password in URI for logging using shared utility
            masked_uri = mask_db_uri(db_uri)
            app.logger.info(f'Database: {masked_uri}')
        else:
            app.logger.warning('SQLALCHEMY_DATABASE_URI not configured')

        # Validate and log ASSETS_ROOT
        assets_root = app.config.get('ASSETS_ROOT', '')
        if assets_root:
            # For URL paths (like /static/assets), verify the physical directory exists
            if assets_root.startswith('/'):
                # Map URL path to physical directory
                # /static/assets -> basedir/infocodest/static/assets
                physical_path = basedir / 'infocodest' / assets_root.lstrip('/')
            else:
                # Absolute path provided
                physical_path = Path(assets_root)

            if not physical_path.exists():
                app.logger.warning(
                    f"ASSETS_ROOT path does not exist: {physical_path}. "
                    "Static assets may not load correctly."
                )
            elif not physical_path.is_dir():
                app.logger.warning(
                    f"ASSETS_ROOT is not a directory: {physical_path}"
                )
            else:
                app.logger.info(f"ASSETS_ROOT validated: {assets_root}")

        # Configure logging level from LOG_LEVEL
        log_level_str = app.config.get('LOG_LEVEL', 'INFO').upper()
        try:
            log_level = getattr(logging, log_level_str)
            app.logger.setLevel(log_level)
            app.logger.info(f"Logging level set to: {log_level_str}")
        except AttributeError:
            app.logger.warning(
                f"Invalid LOG_LEVEL '{log_level_str}'. "
                "Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL. "
                "Defaulting to INFO."
            )
            app.logger.setLevel(logging.INFO)

    @staticmethod
    def init_app(app: 'Flask') -> None:
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
