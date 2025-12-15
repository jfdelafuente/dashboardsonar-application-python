"""
Tests for configuration system.

Tests verify that each configuration class (Development, Testing, Production)
has the correct settings for DEBUG, TESTING, and database URI.
"""
from pathlib import Path
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
    app = create_app(ProductionConfig)

    assert app.config['DEBUG'] is False
    assert app.config['TESTING'] is False
    assert app.config['SQLALCHEMY_DATABASE_URI'] is not None
    # Production falls back to SQLite if DB env vars are not set
    assert 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI'] or 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']
