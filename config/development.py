"""
Development Configuration
=========================

Configuration for development environment.

Created: Phase 6 - Configuration System
Updated: Phase 2 Improvements - Use build_database_uri and configurable DB name
"""

import os
from config.base import BaseConfig, basedir
from config.utils import build_database_uri


class DevelopmentConfig(BaseConfig):
    """Development-specific configuration."""

    # Development mode
    DEBUG = True
    TESTING = False
    DEVELOPMENT = True

    # Database - configurable SQLite filename
    # Use SQLITE_DB_FILE for Development SQLite database (not DB_NAME which is for Production PostgreSQL)
    sqlite_db_file = os.getenv('SQLITE_DB_FILE', 'db.sqlite3')
    SQLALCHEMY_DATABASE_URI = build_database_uri(
        engine='sqlite',
        sqlite_path=basedir / sqlite_db_file
    )
    SQLALCHEMY_ECHO = True  # Show SQL queries in console

    # CSRF (disabled for easier manual testing)
    WTF_CSRF_ENABLED = False

    # Logging
    LOG_LEVEL = 'DEBUG'

    # Debug toolbar
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
