"""
Application entry point.

Loads environment configuration and starts the Flask development server.
For production deployment, use a WSGI server like Gunicorn or uWSGI.

Environment variables:
    DEBUG: Enable debug mode (default: False)
    TESTING: Enable testing mode (default: False)
    HOST: Server host (default: 127.0.0.1)
    PORT: Server port (default: 5000)
"""
import os
from sys import exit
from flask_minify import Minify
from infocodest import create_app
from config import config_dict  # New config system from config/ module (Phase 6)
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Determine environment mode
DEBUG = os.getenv("DEBUG", "False") == "True"
TESTING = os.getenv("TESTING", "False") == "True"

# Select configuration based on environment
if TESTING:
    get_config_mode = "Testing"
elif DEBUG:
    get_config_mode = "Development"
else:
    get_config_mode = "Production"

# Load configuration
try:
    app_config = config_dict[get_config_mode.capitalize()]
except KeyError:
    exit(f"Error: Invalid config mode '{get_config_mode}'. Expected: Development, Production, or Testing")

# Create application
app = create_app(app_config)

# Enable minification in production only
if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)

# Log configuration in debug mode
if DEBUG:
    app.logger.info("DEBUG            = " + str(DEBUG))
    app.logger.info("ENTORNO          = " + get_config_mode.capitalize())
    app.logger.info("Page Compression = " + ("FALSE" if DEBUG else "TRUE"))
    app.logger.info("DBMS             = " + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info("ASSETS_ROOT      = " + app_config.ASSETS_ROOT)

# Run development server
if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=DEBUG
    )
