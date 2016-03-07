from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import jinja2
import markdown

app = Flask(__name__)
app.config.from_object('config')
app.jinja_env.filters['markdown'] = (lambda text:
                                     jinja2.Markup(markdown.markdown(text)))

db = SQLAlchemy(app)

# XXX This layout is somewhat horrible. I will deny to have written this.

from web import models
from web.bots import models
db.create_all()

from web import views
from web.bots import controllers
