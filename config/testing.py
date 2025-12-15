"""
Testing Configuration
=====================

Configuration for testing environment.

Created: Phase 6 - Configuration System
Updated: Phase 2 Improvements - Use build_database_uri and configurable DB name
Updated: Phase 3 Improvements - Add comprehensive type hints
"""

from __future__ import annotations

import os
from typing import ClassVar
from config.base import BaseConfig, basedir
from config.utils import build_database_uri


class TestingConfig(BaseConfig):
    """Testing-specific configuration."""

    # Testing mode
    DEBUG: ClassVar[bool] = True
    TESTING: ClassVar[bool] = True

    # Database - configurable SQLite filename (separate test database)
    # Use SQLITE_DB_FILE for Testing SQLite database (not DB_NAME which is for Production PostgreSQL)
    sqlite_db_file: ClassVar[str] = os.getenv('SQLITE_DB_FILE', 'testdb.sqlite3')
    SQLALCHEMY_DATABASE_URI: ClassVar[str] = build_database_uri(
        engine='sqlite',
        sqlite_path=basedir / sqlite_db_file
    )
    DATABASE: ClassVar[str] = SQLALCHEMY_DATABASE_URI

    # CSRF (disabled for test clients)
    WTF_CSRF_ENABLED: ClassVar[bool] = False

    # Bcrypt (reduced rounds for faster tests)
    BCRYPT_LOG_ROUNDS: ClassVar[int] = 1
