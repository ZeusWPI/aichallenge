from os import path, pardir

basedir = path.abspath(path.join(path.dirname(__file__), pardir))
db_dir = path.join(basedir, 'database', 'db_repository')

WTF_CSRF_ENABLED = False
SECRET_KEY = 'badass'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(db_dir, 'database.db')
SQLALCHEMY_MIGRATE_REPO = db_dir
SQLALCHEMY_TRACK_MODIFICATIONS = False

BOT_CODE_DIR = path.join(basedir, 'bot_code')
