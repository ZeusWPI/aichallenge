import logging
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session as _scoped_session, sessionmaker

from battlebots import config


engine = create_engine(config.SQLALCHEMY_DATABASE_URI, pool_recycle=3600)
engine.dispose()
session_factory = sessionmaker(bind=engine)
Session = _scoped_session(session_factory)

session = Session()


@contextmanager
def scoped_session():
    """Provide a transactional scope around a series of operations."""
    try:
        yield session
        session.commit()
    except:
        logging.exception("Database had to do a rollback.")
        session.rollback()
        raise


# Registers listeners (Don't remove this import!)
import battlebots.database.listeners  # NOQA
