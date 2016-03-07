import os.path

basedir = os.path.abspath(os.path.dirname(__file__))
db_dir = os.path.join(basedir, 'db_repository')

WTF_CSRF_ENABLED = False
SECRET_KEY = 'badass'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(db_dir, 'database.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(db_dir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

BOT_CODE_DIR = os.path.join(basedir, 'bot_code')
