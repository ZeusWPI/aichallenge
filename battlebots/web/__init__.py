import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.wtf.csrf import CsrfProtect
import jinja2
import markdown

from battlebots import config
from battlebots.database import Session

app = Flask(__name__)
app.config.from_object('battlebots.config')
app.jinja_env.filters['markdown'] = (lambda text:
                                     jinja2.Markup(markdown.markdown(text)))
app.jinja_env.tests['not_equalto'] = lambda value, other: value != other

lm = LoginManager(app)
lm.init_app(app)
csrf = CsrfProtect()
csrf.init_app(app)

if config.PRODUCTION:
    log_file_handler = RotatingFileHandler(config.WEB_LOG, maxBytes=10000000)
    logging.getLogger().addHandler(log_file_handler)
    logging.getLogger('werkzeug').addHandler(log_file_handler)
    app.logger.addHandler(log_file_handler)
    # TODO add airbrake

app.before_request(lambda: Session.remove())

from battlebots.web import views  # NOQA
from battlebots.web.views import bots  # NOQA
