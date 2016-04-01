import jinja2
import markdown
from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.wtf.csrf import CsrfProtect

app = Flask(__name__)
app.config.from_object('battlebots.config')
app.jinja_env.filters['markdown'] = (lambda text:
                                     jinja2.Markup(markdown.markdown(text)))
app.jinja_env.tests['not_equalto'] = lambda value, other: value != other

lm = LoginManager(app)
lm.init_app(app)
csrf = CsrfProtect()
csrf.init_app(app)

from battlebots.web import views
from battlebots.web.views import bots
