import os
import shutil
import logging

from battlebots import config
from battlebots.database import scoped_session


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


def remove_bot(bot):
    code_dir = os.path.join(config.BOT_CODE_DIR, bot.user.nickname, bot.name)
    try:
        shutil.rmtree(code_dir)
    except FileNotFoundError:
        # Don't crash if for some reason this dir doesn't exist anymore
        logging.warning('Code dir of bot %s:%s not found (%s)'
                        % (bot.user.nickname, bot.name, code_dir))
        pass

    delete(bot)
