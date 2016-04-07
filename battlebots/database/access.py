import os
import shutil
import logging

from battlebots import config
from battlebots.database import session, scoped_session
from battlebots.database.models import Bot


def add(instance):
    with scoped_session() as db:
        db.add(instance)


def add_all(instances):
    with scoped_session() as db:
        db.add_all(instances)


def delete(instance):
    with scoped_session() as db:
        db.delete(instance)


def merge(instance, load=True):
    with scoped_session() as db:
        db.merge(instance, load=load)


def remove_bot(user, botname):
    code_dir = os.path.join(config.BOT_CODE_DIR, user.nickname, botname)
    try:
        shutil.rmtree(code_dir)
    except FileNotFoundError:
        # Don't crash if for some reason this dir doesn't exist anymore
        logging.warning('Code dir of bot %s:%s not found (%s)'
                        % (user.nickname, botname, code_dir))
        pass

    bot = session.query(Bot).filter_by(user=user, name=botname).one_or_none()
    if bot is None:
        logging.warning(
            'Trying to remove a bot that does not exist. User:{}, Bot:{}'
            .format(user, botname))
        return

    delete(bot)
