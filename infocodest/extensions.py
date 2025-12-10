from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
  pass


db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
migrate = Migrate()
bootstrap = Bootstrap()
csrf = CSRFProtect()

login_manager.login_view = "accounts.login"
login_manager.login_message_category = "danger"

from infocodest.models.users import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()