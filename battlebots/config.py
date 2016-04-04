import logging
from os import path

BASE_DIR = path.abspath(path.dirname(__file__))
REPO_ROOT = path.dirname(BASE_DIR)
DB_DIR = path.join(BASE_DIR, 'database')
BOT_CODE_DIR = path.join(BASE_DIR, 'bots')
MATCH_LOG_DIR = path.join(BASE_DIR, 'logs')
RANKER_LOG = path.join(BASE_DIR, 'ranker.log')

SECRET_KEY = 'badass'
LOG_LEVEL = logging.INFO

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(DB_DIR, 'database.db')
