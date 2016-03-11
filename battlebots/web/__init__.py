from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
import jinja2
import markdown


app = Flask(__name__)
app.config.from_object('battlebots.config')
app.jinja_env.filters['markdown'] = (lambda text:
                                     jinja2.Markup(markdown.markdown(text)))

db = SQLAlchemy(app)
lm = LoginManager(app)
lm.init_app(app)


from battlebots.database import models
db.create_all()


from battlebots.web import views
from battlebots.web.bots import controllers
