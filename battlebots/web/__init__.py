from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
import jinja2
import markdown

app = Flask(__name__)
app.config.from_object('config')
app.jinja_env.filters['markdown'] = (lambda text:
                                     jinja2.Markup(markdown.markdown(text)))

db = SQLAlchemy(app)
lm = LoginManager(app)
lm.init_app(app)
# XXX This layout is somewhat horrible. I will deny to have written this.


from battlebots.web import views
from battlebots.web.bots import controllers