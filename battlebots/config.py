import logging
import os
from os import path

PRODUCTION = False

BASE_DIR = path.abspath(path.dirname(__file__))
REPO_ROOT = path.dirname(BASE_DIR)
DB_DIR = path.join(BASE_DIR, 'database')
BOT_CODE_DIR = path.join(BASE_DIR, 'bots')
MATCH_LOG_DIR = path.join(BASE_DIR, 'matches')

if PRODUCTION:
    LOG_LEVEL = logging.WARNING
    LOGS_HOME = path.join(os.environ['HOME'], 'log')
else:
    LOG_LEVEL = logging.INFO
    LOGS_HOME = REPO_ROOT
RANKER_LOG = path.join(LOGS_HOME, 'ranker.log')
WEB_LOG = path.join(LOGS_HOME, 'web.log')

SECRET_KEY = 'badass'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(DB_DIR, 'database.db')

AIRBRAKE_BASE_URL = 'http://errbit.awesomepeople.tv'
AIRBRAKE_ID = '57056f3b6b696e20df00002d'
AIRBRAKE_KEY = '4199e1aa858bcea3022120a2848fc898'
