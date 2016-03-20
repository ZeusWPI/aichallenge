from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.wtf.csrf import CsrfProtect
import jinja2
import markdown


app = Flask(__name__)
app.config.from_object('battlebots.config')
app.jinja_env.filters['markdown'] = (lambda text:
                                     jinja2.Markup(markdown.markdown(text)))

lm = LoginManager(app)
lm.init_app(app)
csrf = CsrfProtect()
csrf.init_app(app)

from battlebots.database import models

from battlebots.web import views
from battlebots.web.bots import controllers
