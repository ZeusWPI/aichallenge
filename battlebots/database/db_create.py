import os.path
from migrate.versioning import api

from battlebots.config import SQLALCHEMY_DATABASE_URI
from battlebots.config import SQLALCHEMY_MIGRATE_REPO
from battlebots.web import db

print("Creating new Battlebots databees")
if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(SQLALCHEMY_DATABASE_URI,
                        SQLALCHEMY_MIGRATE_REPO,
                        api.version(SQLALCHEMY_MIGRATE_REPO))
db.create_all()
