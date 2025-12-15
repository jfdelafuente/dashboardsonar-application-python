"""
Testing Configuration
=====================

Configuration for testing environment.

Created: Phase 6 - Configuration System
Updated: Phase 2 Improvements - Use build_database_uri and configurable DB name
"""

import os
from config.base import BaseConfig, basedir
from config.utils import build_database_uri


class TestingConfig(BaseConfig):
    """Testing-specific configuration."""

    # Testing mode
    DEBUG = True
    TESTING = True

    # Database - configurable SQLite filename (separate test database)
    db_name = os.getenv('DB_NAME', 'testdb.sqlite3')
    SQLALCHEMY_DATABASE_URI = build_database_uri(
        engine='sqlite',
        sqlite_path=basedir / db_name
    )
    DATABASE = SQLALCHEMY_DATABASE_URI

    # CSRF (disabled for test clients)
    WTF_CSRF_ENABLED = False

    # Bcrypt (reduced rounds for faster tests)
    BCRYPT_LOG_ROUNDS = 1
