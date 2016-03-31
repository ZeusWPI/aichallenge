import logging
from os import path

BASE_DIR = path.abspath(path.dirname(__file__))
DB_DIR = path.join(BASE_DIR, 'database')
BOT_CODE_DIR = path.join(BASE_DIR, 'bots')
MATCH_LOG_DIR = path.join(BASE_DIR, 'logs')
SANDBOX_CMD = path.join(BASE_DIR, 'sandbox', 'run.sh')

SECRET_KEY = 'badass'
LOG_LEVEL = logging.INFO

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(DB_DIR, 'database.db')
SQLALCHEMY_MIGRATE_REPO = path.join(DB_DIR, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False
