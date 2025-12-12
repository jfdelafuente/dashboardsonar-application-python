"""
Testing Configuration
=====================

Configuration for testing environment.

Created: Phase 6 - Configuration System
"""

import os
from config.base import BaseConfig, basedir


class TestingConfig(BaseConfig):
    """Testing-specific configuration."""

    # Testing mode
    DEBUG = True
    TESTING = True

    # Database (separate test database)
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'testdb.sqlite3'}"
    DATABASE = f"sqlite:///{basedir / 'testdb.sqlite3'}"

    # CSRF (disabled for test clients)
    WTF_CSRF_ENABLED = False

    # Bcrypt (reduced rounds for faster tests)
    BCRYPT_LOG_ROUNDS = 1
