"""
Application entry point.

Loads environment configuration and starts the Flask development server.
For production deployment, use a WSGI server like Gunicorn or uWSGI.

Environment variables:
    DEBUG: Enable debug mode (default: False)
    TESTING: Enable testing mode (default: False)
    HOST: Server host (default: 127.0.0.1)
    PORT: Server port (default: 5000)

Updated: Phase 1 Improvements - Use shared utilities from config.utils
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from infocodest import create_app
from config import config_dict
from config.utils import str_to_bool, mask_db_uri


def get_port(default: int = 5000) -> int:
    """
    Get and validate port number from environment.

    Args:
        default: Default port number

    Returns:
        Valid port number (1024-65535)
    """
    try:
        port = int(os.getenv("PORT", str(default)))
        if not (1024 <= port <= 65535):
            print(f"Warning: Invalid PORT {port}, using {default}")
            return default
        return port
    except ValueError:
        print(f"Warning: Invalid PORT value, using {default}")
        return default


# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Determine environment mode using safe boolean parsing
DEBUG = str_to_bool(os.getenv("DEBUG"), default=False)
TESTING = str_to_bool(os.getenv("TESTING"), default=False)

# Select configuration based on environment
if TESTING:
    config_mode = "Testing"
elif DEBUG:
    config_mode = "Development"
else:
    config_mode = "Production"

# Load configuration
try:
    app_config = config_dict[config_mode]
except KeyError:
    sys.exit(f"Error: Invalid config mode '{config_mode}'. Expected: Development, Production, or Testing")

# Create application
app = create_app(app_config)

# Enable minification in production only
if not DEBUG:
    from flask_minify import Minify
    Minify(app=app, html=True, js=False, cssless=False)

# Log configuration in debug mode
if DEBUG:
    app.logger.info(f"DEBUG            = {DEBUG}")
    app.logger.info(f"ENVIRONMENT      = {config_mode}")
    app.logger.info(f"Page Compression = {not DEBUG}")
    app.logger.info(f"DBMS             = {mask_db_uri(app_config.SQLALCHEMY_DATABASE_URI)}")
    app.logger.info(f"ASSETS_ROOT      = {app_config.ASSETS_ROOT}")

# Run development server
if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=get_port(),
        debug=DEBUG
    )
