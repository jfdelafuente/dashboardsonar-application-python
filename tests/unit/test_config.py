"""
Tests for configuration system.

Tests verify that each configuration class (Development, Testing, Production)
has the correct settings for DEBUG, TESTING, and database URI.
"""
import os
from pathlib import Path
from unittest.mock import patch
from infocodest import create_app
from config import DevelopmentConfig, TestingConfig, ProductionConfig


basedir = Path(__file__).resolve().parent.parent.parent


def test_development_config():
    """Test Development configuration has correct settings."""
    app = create_app(DevelopmentConfig)

    assert app.config['DEBUG'] is True
    assert app.config['TESTING'] is False
    assert app.config['DEVELOPMENT'] is True
    assert 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']
    assert app.config['WTF_CSRF_ENABLED'] is False
    assert app.config['SQLALCHEMY_ECHO'] is True


def test_testing_config():
    """Test Testing configuration has correct settings."""
    app = create_app(TestingConfig)

    assert app.config['DEBUG'] is True
    assert app.config['TESTING'] is True
    assert 'testdb.sqlite3' in app.config['SQLALCHEMY_DATABASE_URI']
    assert app.config['WTF_CSRF_ENABLED'] is False
    assert app.config['BCRYPT_LOG_ROUNDS'] == 1


def test_production_config():
    """Test Production configuration has correct settings."""
    # Production requires SECRET_KEY for init_app validation
    # Generate a valid test secret key (32+ characters)
    test_secret_key = 'test-secret-key-for-unit-testing-minimum-32-chars-required'

    # Use SQLite for testing (avoid requiring PostgreSQL in test environment)
    test_db_uri = f'sqlite:///{basedir}/test-production-db.sqlite3'

    # Patch SECRET_KEY and SQLALCHEMY_DATABASE_URI for testing
    with patch.object(ProductionConfig, 'SECRET_KEY', test_secret_key), \
         patch.object(ProductionConfig, 'SQLALCHEMY_DATABASE_URI', test_db_uri):
        app = create_app(ProductionConfig)

        assert app.config['DEBUG'] is False
        assert app.config['TESTING'] is False
        assert app.config['SECRET_KEY'] == test_secret_key
        assert app.config['SQLALCHEMY_DATABASE_URI'] is not None
        # Verify using the test SQLite database
        assert 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']
