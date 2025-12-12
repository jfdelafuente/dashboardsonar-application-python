"""
Configuration Module
====================

Modular configuration system for Flask application.

Provides environment-specific configurations:
- Development: Local development with debug enabled
- Testing: Test environment with test database
- Production: Production with security hardening

Usage:
    from config import config_dict

    config = config_dict['Development']
    app = create_app(config)

Created: Phase 6 - Configuration System
"""

from config.base import BaseConfig
from config.development import DevelopmentConfig
from config.testing import TestingConfig
from config.production import ProductionConfig

# Configuration dictionary for easy lookup
config_dict = {
    'Production': ProductionConfig,
    'Testing': TestingConfig,
    'Development': DevelopmentConfig,
    'base': BaseConfig
}

__all__ = [
    'BaseConfig',
    'DevelopmentConfig',
    'TestingConfig',
    'ProductionConfig',
    'config_dict'
]
