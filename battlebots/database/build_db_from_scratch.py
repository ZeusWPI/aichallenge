#!/usr/bin/env python3
import os

import alembic
from alembic.config import Config

from battlebots import config
from battlebots.database import engine
from battlebots.database.models import Base


# Remove possibly existing old database
Base.metadata.drop_all(engine)

# Create tables in new datbase
Base.metadata.create_all(engine)

# Load the Alembic configuration and generate the version table, "stamping" it
# with the most recent rev
alembic_config = Config(os.path.join(config.DB_DIR, 'alembic.ini'))
alembic.command.stamp(alembic_config, "head")
