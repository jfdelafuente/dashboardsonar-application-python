import os
from sys import exit
# from flask_migrate import Migrate
from flask_minify import Minify
from infocodest import create_app
from config import config_dict
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# WARNING: Don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False") == "True"

# The configuration
get_config_mode = "Development" if DEBUG else "Production"

try:
    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]
except KeyError:
    exit("Error: Invalid <config_mode>. Expected values [Development, Production] ")

app = create_app(app_config)
# Migrate(app, db)

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)

if DEBUG:
    app.logger.info("DEBUG            = " + str(DEBUG))
    app.logger.info("ENTORNO          = " + get_config_mode.capitalize())
    # app.logger.info("FLASK_ENV        = " + app_config.FLASK_ENV)
    app.logger.info("Page Compression = " + "FALSE" if DEBUG else "TRUE")
    app.logger.info("DBMS             = " + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info("ASSETS_ROOT      = " + app_config.ASSETS_ROOT)

if __name__ == "__main__":
    app.run()
