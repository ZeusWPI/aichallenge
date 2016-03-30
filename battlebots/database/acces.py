import os
import shutil
import logging

from battlebots import config
from battlebots.database import session
from battlebots.database.models import Bot


def add(instance):
    session.add(instance)
    session.commit()


def delete(instance):
    session.delete(instance)
    session.commit()


def remove_bot(user, botname):
    code_dir = os.path.join(config.BOT_CODE_DIR, user.nickname, botname)
    try:
        shutil.rmtree(code_dir)
    except FileNotFoundError:
        # Don't crash if for some reason this dir doesn't exist anymore
        logging.warning('Code dir of bot %s:%s not found (%s)'
                        % (user.nickname, botname, code_dir))
        pass

    bot = session.query(Bot).filter_by(user=user, name=botname).one()
    delete(bot)
