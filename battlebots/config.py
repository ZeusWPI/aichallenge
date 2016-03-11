from os import path

BASE_DIR = path.abspath(path.dirname(__file__))
DB_DIR = path.join(BASE_DIR, 'database')
BOT_CODE_DIR = path.join(BASE_DIR, 'bots')

SECRET_KEY = 'badass'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(DB_DIR, 'database.db')
SQLALCHEMY_MIGRATE_REPO = path.join(DB_DIR, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False
