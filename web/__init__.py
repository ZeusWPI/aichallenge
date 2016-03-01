from flask import Flask
from flask_login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from flask_user import UserManager, UserMixin, SQLAlchemyAdapter

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)

from web.models import User
# Setup Flask-User
db_adapter = SQLAlchemyAdapter(db, User)        # Register the User model
user_manager = UserManager(db_adapter, app)     # Initialize Flask-User

from web import views
