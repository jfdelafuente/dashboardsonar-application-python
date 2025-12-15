"""
Development Configuration
=========================

Configuration for development environment.

Created: Phase 6 - Configuration System
Updated: Phase 2 Improvements - Use build_database_uri and configurable DB name
Updated: Phase 3 Improvements - Add comprehensive type hints
"""

from __future__ import annotations

import os
from typing import ClassVar
from config.base import BaseConfig, basedir
from config.utils import build_database_uri


class DevelopmentConfig(BaseConfig):
    """Development-specific configuration."""

    # Development mode
    DEBUG: ClassVar[bool] = True
    TESTING: ClassVar[bool] = False
    DEVELOPMENT: ClassVar[bool] = True

    # Database - configurable SQLite filename
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
