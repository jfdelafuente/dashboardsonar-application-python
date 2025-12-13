"""
Development Configuration
=========================

Configuration for development environment.

Created: Phase 6 - Configuration System
"""

import os
from config.base import BaseConfig, basedir


class DevelopmentConfig(BaseConfig):
    """Development-specific configuration."""

    # Development mode
    DEBUG = True
    TESTING = False
    DEVELOPMENT = True

    # Database
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'db.sqlite3'}"
    SQLALCHEMY_ECHO = True  # Show SQL queries in console

    # CSRF (disabled for easier manual testing)
    WTF_CSRF_ENABLED = False

    # Logging
    LOG_LEVEL = 'DEBUG'

    # Debug toolbar
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
