"""
Development Configuration
=========================

Configuration for development environment.

Created: Phase 6 - Configuration System
Updated: Phase 2 Improvements - Use build_database_uri and configurable DB name
Updated: Phase 3 Improvements - Add comprehensive type hints
Updated: Auto-detect PostgreSQL vs SQLite based on environment variables
"""

from __future__ import annotations

import os
from typing import ClassVar, Optional
from config.base import BaseConfig, basedir
from config.utils import build_database_uri


class DevelopmentConfig(BaseConfig):
    """Development-specific configuration.

    Auto-detects database type:
    - If DB_ENGINE and DB_USERNAME are set: uses PostgreSQL/MySQL
    - Otherwise: uses SQLite (default)
    """

    # Development mode
    DEBUG: ClassVar[bool] = True
    TESTING: ClassVar[bool] = False
    DEVELOPMENT: ClassVar[bool] = True

    # Database - Auto-detect PostgreSQL vs SQLite
    # Check if PostgreSQL/MySQL variables are configured
    DB_ENGINE: ClassVar[Optional[str]] = os.getenv('DB_ENGINE')
    DB_USERNAME: ClassVar[Optional[str]] = os.getenv('DB_USERNAME')

    # Determine which database to use based on environment variables
    if DB_ENGINE and DB_ENGINE.lower() != 'sqlite' and DB_USERNAME:
        # Use PostgreSQL/MySQL from environment variables
        DB_PASSWORD: ClassVar[Optional[str]] = os.getenv('DB_PASS')
        DB_HOST: ClassVar[Optional[str]] = os.getenv('DB_HOST', 'localhost')
        DB_PORT: ClassVar[Optional[str]] = os.getenv('DB_PORT')
        DB_NAME: ClassVar[Optional[str]] = os.getenv('DB_NAME', 'dashboardsonar_dev')

        # Build PostgreSQL/MySQL URI
        SQLALCHEMY_DATABASE_URI: ClassVar[str] = build_database_uri(
            engine=DB_ENGINE,
            username=DB_USERNAME,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=int(DB_PORT) if DB_PORT else None,
            database=DB_NAME
        )
    else:
        # Default: SQLite
        # Use SQLITE_DB_FILE for Development SQLite database (not DB_NAME which is for Production PostgreSQL)
        sqlite_db_file: ClassVar[str] = os.getenv('SQLITE_DB_FILE', 'db.sqlite3')
        SQLALCHEMY_DATABASE_URI: ClassVar[str] = build_database_uri(
            engine='sqlite',
            sqlite_path=basedir / sqlite_db_file
        )

    SQLALCHEMY_ECHO: ClassVar[bool] = True  # Show SQL queries in console

    # CSRF (disabled for easier manual testing)
    WTF_CSRF_ENABLED: ClassVar[bool] = False

    # Logging
    LOG_LEVEL: ClassVar[str] = 'DEBUG'

    # Debug toolbar
    DEBUG_TB_ENABLED: ClassVar[bool] = True
    DEBUG_TB_INTERCEPT_REDIRECTS: ClassVar[bool] = False
