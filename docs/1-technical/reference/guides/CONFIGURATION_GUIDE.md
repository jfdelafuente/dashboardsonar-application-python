# Configuration Guide

**Version**: 1.6.0
**Created**: Phase 6 - Configuration System
**Last Updated**: 2025-12-12

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Configuration Classes](#configuration-classes)
- [Environment Variables](#environment-variables)
- [Usage Examples](#usage-examples)
- [Validation](#validation)
- [Security Best Practices](#security-best-practices)
- [Migration Guide](#migration-guide)
- [Troubleshooting](#troubleshooting)

---

## Overview

The Dashboard Sonar application uses a modular configuration system organized by environment. This approach provides:

- **Separation of concerns**: Each environment has its own configuration file
- **Inheritance**: Common settings defined once in BaseConfig
- **Type safety**: Using type hints and Path objects
- **Validation**: Automatic validation on app initialization
- **Security**: Secure handling of secrets and credentials

### Key Features

✅ Environment-specific configurations (Development, Testing, Production)
✅ Automatic configuration validation with logging
✅ Secure SECRET_KEY generation
✅ Multi-DBMS support (SQLite, PostgreSQL, MySQL)
✅ Password masking in logs
✅ Flexible environment variable management

---

## Architecture

### Directory Structure

```
config/
├── __init__.py           # Module exports and config_dict
├── base.py              # BaseConfig - shared settings
├── development.py       # DevelopmentConfig
├── testing.py           # TestingConfig
└── production.py        # ProductionConfig
```

### Inheritance Hierarchy

```
BaseConfig (base.py)
├── DevelopmentConfig (development.py)
├── TestingConfig (testing.py)
└── ProductionConfig (production.py)
```

All environment-specific configs inherit from `BaseConfig`, which contains shared settings like security, logging, and session configuration.

---

## Configuration Classes

### BaseConfig

**File**: [config/base.py](../../config/base.py)

Shared configuration for all environments.

**Key Settings**:

| Setting | Default | Description |
|---------|---------|-------------|
| `SECRET_KEY` | Auto-generated | Flask secret key (from env or generated) |
| `CSRF_ENABLED` | `True` | Enable CSRF protection |
| `WTF_CSRF_ENABLED` | `True` | Enable WTF-CSRF |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | `False` | Disable modification tracking |
| `SQLALCHEMY_ECHO` | `False` | SQL query logging |
| `BCRYPT_LOG_ROUNDS` | `13` | Password hashing rounds |
| `ASSETS_ROOT` | `/static/assets` | Static assets path |
| `FLASK_APP` | `run.py` | Flask entry point |
| `DAYS_COMPARISON` | `15` | Dashboard comparison period |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_DIR` | `logs/` | Log directory |
| `SESSION_COOKIE_HTTPONLY` | `True` | HTTP-only session cookies |
| `REMEMBER_COOKIE_HTTPONLY` | `True` | HTTP-only remember cookies |
| `REMEMBER_COOKIE_DURATION` | `3600` | Remember cookie lifetime (seconds) |

**Methods**:

- `validate_config(app)`: Validates configuration and logs status (without exposing secrets)
- `init_app(app)`: Hook for custom initialization (calls validate_config by default)

### DevelopmentConfig

**File**: [config/development.py](../../config/development.py)

Configuration for local development.

**Key Settings**:

| Setting | Value | Description |
|---------|-------|-------------|
| `DEBUG` | `True` | Enable debug mode |
| `DEVELOPMENT` | `True` | Development flag |
| `SQLALCHEMY_DATABASE_URI` | `sqlite:///db.sqlite3` | Local SQLite database |
| `SQLALCHEMY_ECHO` | `True` | Show SQL queries in console |
| `WTF_CSRF_ENABLED` | `False` | CSRF disabled for easier testing |
| `LOG_LEVEL` | `DEBUG` | Verbose logging |
| `DEBUG_TB_ENABLED` | `True` | Enable debug toolbar |

**Use Case**: Local development, debugging, rapid prototyping

### TestingConfig

**File**: [config/testing.py](../../config/testing.py)

Configuration for automated testing.

**Key Settings**:

| Setting | Value | Description |
|---------|-------|-------------|
| `DEBUG` | `True` | Enable debug for test output |
| `TESTING` | `True` | Testing flag |
| `SQLALCHEMY_DATABASE_URI` | `sqlite:///testdb.sqlite3` | Separate test database |
| `WTF_CSRF_ENABLED` | `False` | CSRF disabled for testing |
| `BCRYPT_LOG_ROUNDS` | `1` | Reduced for faster tests |

**Use Case**: Unit tests, integration tests, CI/CD pipelines

### ProductionConfig

**File**: [config/production.py](../../config/production.py)

Configuration for production deployment.

**Key Settings**:

| Setting | Value | Description |
|---------|-------|-------------|
| `DEBUG` | `False` | Disable debug mode |
| `SQLALCHEMY_DATABASE_URI` | From env vars | PostgreSQL/MySQL or SQLite fallback |
| `SESSION_COOKIE_SECURE` | `True` | HTTPS-only cookies |
| `REMEMBER_COOKIE_SECURE` | `True` | HTTPS-only remember cookies |
| `DEBUG_TB_ENABLED` | `False` | Debug toolbar disabled |

**Database Configuration**:

Production supports multiple database engines configured via environment variables:

```python
# Required for PostgreSQL/MySQL
DB_ENGINE=postgresql  # or mysql
DB_USERNAME=dbuser
DB_PASS=dbpassword
DB_HOST=localhost
DB_PORT=5432         # or 3306 for MySQL
DB_NAME=dashboardsonar

# If not set, falls back to SQLite
```

**Use Case**: Production deployment, staging environments

---

## Environment Variables

### Configuration File

Create a `.env` file in the project root (see [.env.example](../../.env.example)):

```bash
# Database Configuration
DB_ENGINE=postgresql
DB_USERNAME=dbuser
DB_PASS=dbpassword
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dashboardsonar

# Security
SECRET_KEY=your-secret-key-here-change-in-production

# Application Settings
FLASK_APP=run.py
DEBUG=False
DAYS_COMPARISON=15

# Logging
LOG_LEVEL=INFO

# Assets
ASSETS_ROOT=/static/assets
```

### Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Recommended | Auto-generated | Flask secret key for sessions/CSRF |
| `DB_ENGINE` | Production only | - | Database engine (postgresql, mysql) |
| `DB_USERNAME` | Production only | - | Database username |
| `DB_PASS` | Production only | - | Database password |
| `DB_HOST` | Production only | - | Database host |
| `DB_PORT` | Production only | - | Database port |
| `DB_NAME` | Production only | - | Database name |
| `DEBUG` | No | `False` | Enable debug mode |
| `FLASK_APP` | No | `run.py` | Flask entry point |
| `DAYS_COMPARISON` | No | `15` | Dashboard comparison period |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `ASSETS_ROOT` | No | `/static/assets` | Static assets path |

### Loading Environment Variables

The application uses `python-decouple` to load environment variables:

```python
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
```

This automatically finds and loads the `.env` file.

---

## Usage Examples

### Basic Usage

**In run.py or application factory**:

```python
from config import config_dict

# Select configuration by environment
config_mode = 'Development'  # or 'Testing', 'Production'
app_config = config_dict[config_mode]

# Create Flask app with config
app = create_app(app_config)
```

### Dynamic Environment Selection

```python
import os
from config import config_dict

# Select based on DEBUG environment variable
DEBUG = os.getenv('DEBUG', 'False') == 'True'
config_mode = 'Development' if DEBUG else 'Production'

app_config = config_dict[config_mode.capitalize()]
app = create_app(app_config)
```

### Accessing Configuration in Application

```python
from flask import current_app

# Access configuration values
secret_key = current_app.config['SECRET_KEY']
debug_mode = current_app.config['DEBUG']
db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
days = current_app.config['DAYS_COMPARISON']
```

### Custom Initialization Hook

```python
from config.base import BaseConfig

class CustomConfig(BaseConfig):
    """Custom configuration with additional setup."""

    CUSTOM_SETTING = 'custom_value'

    @staticmethod
    def init_app(app):
        """Custom initialization."""
        # Call parent validation
        BaseConfig.validate_config(app)

        # Add custom setup
        app.logger.info('Custom configuration loaded')

        # Set up custom handlers, extensions, etc.
        # ...
```

### Testing Configuration

```python
import unittest
from config import config_dict
from infocodest import create_app

class ConfigTestCase(unittest.TestCase):

    def test_development_config(self):
        """Test development configuration."""
        app = create_app(config_dict['Development'])

        self.assertTrue(app.config['DEBUG'])
        self.assertTrue(app.config['DEVELOPMENT'])
        self.assertFalse(app.config['TESTING'])
        self.assertIn('sqlite', app.config['SQLALCHEMY_DATABASE_URI'])

    def test_production_config(self):
        """Test production configuration."""
        app = create_app(config_dict['Production'])

        self.assertFalse(app.config['DEBUG'])
        self.assertFalse(app.config['TESTING'])
        self.assertTrue(app.config['SESSION_COOKIE_SECURE'])
```

---

## Validation

### Automatic Validation

Configuration is automatically validated when the app initializes via the `init_app()` hook:

```python
app = create_app(app_config)
# Validation runs automatically
```

**What gets validated**:

1. ✅ Configuration class name is logged
2. ✅ Debug/Testing mode is logged
3. ✅ SECRET_KEY existence is checked (warning if auto-generated)
4. ✅ Database URI is logged (with masked password)

### Example Validation Output

```
[INFO] Configuration loaded: DevelopmentConfig
[INFO] Debug mode: True
[INFO] Testing mode: False
[INFO] Database: sqlite:////path/to/db.sqlite3
```

### Manual Validation

You can manually validate configuration:

```python
from config.base import BaseConfig

# After creating app
BaseConfig.validate_config(app)
```

### Verification Script

Run the configuration verification script to test all configs:

```bash
python scripts/verify_config.py
```

**Tests performed**:

1. Import all config classes
2. Verify config_dict structure
3. Verify required attributes
4. Verify inheritance hierarchy
5. Verify environment-specific settings

---

## Security Best Practices

### 1. SECRET_KEY Management

**❌ Bad**:
```python
SECRET_KEY = 'hardcoded-secret'  # NEVER do this
```

**✅ Good**:
```python
# In .env
SECRET_KEY=generated-secure-random-key-here

# In code (already handled by BaseConfig)
SECRET_KEY = os.getenv('SECRET_KEY', None)
if not SECRET_KEY:
    SECRET_KEY = secrets.token_hex(32)  # Auto-generate if missing
```

**Generate secure keys**:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Database Credentials

**❌ Bad**:
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/db'
```

**✅ Good**:
```bash
# In .env (NEVER commit this file)
DB_ENGINE=postgresql
DB_USERNAME=user
DB_PASS=secure_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dbname
```

### 3. Environment Files

- ✅ Keep `.env` in `.gitignore`
- ✅ Provide `.env.example` with dummy values
- ✅ Use different `.env` files for each environment
- ✅ Never commit real credentials to version control

### 4. Production Settings

**Essential production settings**:

```python
DEBUG = False                      # Never True in production
TESTING = False                    # Never True in production
SESSION_COOKIE_SECURE = True       # HTTPS only
REMEMBER_COOKIE_SECURE = True      # HTTPS only
SESSION_COOKIE_HTTPONLY = True     # Prevent XSS
REMEMBER_COOKIE_HTTPONLY = True    # Prevent XSS
```

### 5. Logging Safely

The configuration system automatically masks passwords in logs:

```python
# Database URI in config
SQLALCHEMY_DATABASE_URI = 'postgresql://user:secret@localhost/db'

# Logged as (password masked)
Database: postgresql://user:****@localhost/db
```

---

## Migration Guide

### From Old config.py to New config/ Module

The old monolithic `config.py` is deprecated as of Phase 6. Migration is simple because the import interface remains the same.

#### Step 1: No Code Changes Needed

**Your existing code**:
```python
from config import config_dict

app_config = config_dict['Development']
app = create_app(app_config)
```

**Still works!** The new `config/` module exports the same interface.

#### Step 2: Update Environment Variables (Optional)

The new system supports additional environment variables:

```bash
# Old .env
SECRET_KEY=...
DEBUG=True

# New .env (add these)
SECRET_KEY=...
DEBUG=True
FLASK_APP=run.py
DAYS_COMPARISON=15
LOG_LEVEL=INFO
```

#### Step 3: Remove Old config.py (Phase 10)

The old `config.py` will be removed in Phase 10. Until then, it's kept for backward compatibility.

#### Migration Checklist

- [x] Update `.env` with new variables (see `.env.example`)
- [x] Test application with new config: `python scripts/verify_config.py`
- [x] Review configuration validation output in logs
- [ ] Remove old `config.py` (scheduled for Phase 10)

---

## Troubleshooting

### Issue: Import Error

**Error**:
```
ImportError: No module named 'config'
```

**Solution**:
Ensure project root is in Python path:

```python
import sys
import os
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from config import config_dict
```

### Issue: SECRET_KEY Warning

**Warning**:
```
[WARNING] SECRET_KEY not set - using generated key
```

**Solution**:
Set SECRET_KEY in `.env`:

```bash
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
echo "SECRET_KEY=$SECRET_KEY" >> .env
```

### Issue: Database Connection Failed

**Error**:
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution**:
Check database configuration in `.env`:

```bash
# Verify all database variables are set
DB_ENGINE=postgresql
DB_USERNAME=correct_user
DB_PASS=correct_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=correct_dbname
```

**Test connection**:
```python
from sqlalchemy import create_engine
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
engine.connect()  # Should succeed
```

### Issue: Configuration Not Loading

**Problem**: Changes to `.env` not reflected

**Solution**:
1. Ensure `.env` is in project root
2. Restart Flask application
3. Check `.env` is loaded:

```python
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import os
print(os.getenv('SECRET_KEY'))  # Should print your key
```

### Issue: CSRF Errors in Development

**Error**:
```
flask_wtf.csrf.CSRFError: The CSRF token is missing
```

**Solution**:
CSRF is disabled in DevelopmentConfig. Ensure you're using the correct config:

```python
# run.py
DEBUG = os.getenv("DEBUG", "False") == "True"
config_mode = "Development" if DEBUG else "Production"

# Verify
print(f"Using {config_mode} configuration")
```

### Issue: Verification Script Fails

**Error**:
```
[FAIL] Missing attributes: ['SQLALCHEMY_DATABASE_URI']
```

**Solution**:
This is expected for BaseConfig (it doesn't define SQLALCHEMY_DATABASE_URI). Environment-specific configs (Development, Testing, Production) should all pass.

Run the verification script:
```bash
python scripts/verify_config.py
```

All environment configs should show `[OK]`.

---

## Additional Resources

### Documentation

- [Configuration Module Source](../../config/)
- [Environment Example](.env.example)
- [Verification Script](../../scripts/verify_config.py)
- [Phase 6 Detailed Plan](../plan/FASE_6_PLAN_DETALLADO.md)

### External References

- [Flask Configuration Documentation](https://flask.palletsprojects.com/en/2.3.x/config/)
- [Python Decouple](https://pypi.org/project/python-decouple/)
- [SQLAlchemy Database URLs](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)

### Related Phases

- **Phase 5**: Service Layer Implementation
- **Phase 6**: Configuration System (current)
- **Phase 7**: Advanced Security & Logging (next)

---

**Document Version**: 1.0
**Last Updated**: 2025-12-12
**Maintained by**: Dashboard Sonar Team
