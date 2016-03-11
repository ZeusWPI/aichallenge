#!/usr/bin/env python
import contextlib
import json
import logging
import os.path
import subprocess as sp

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.sql.expression import func

from battlebots.database.models import User, Bot

from battlebots import config
from battlebots.arbiter import arbiter

MAX_STEPS = 500


@contextlib.contextmanager
def in_dir(directory):
    prev_dir = os.getcwd()
    os.chdir(directory)
    yield
    os.chdir(prev_dir)


def battle_on():
    db = db_session()

    bot1 = db.query(Bot).order_by(func.random()).first()
    bot2 = db.query(Bot).order_by(func.random()).first()

    # TODO compile async
    compilation_success = all(bot.compile() for bot in (bot1, bot2))
    if not compilation_success:
        # Save errors on bots
        db.add_all((bot1, bot2))
        db.commit()
        logging.warn('Compilation failed')
        return

    # TODO generate new map instead of a fixed one
    map_filename = os.path.abspath(__file__ + '/../../arbiter/map.input')

    log_filename = 'match.log'
    config = {
        'players': {
            bot1.full_name: bot1.sandboxed_run_cmd,
            # TODO remove the v2 once we select two different bots
            bot2.full_name + ' v2': bot2.sandboxed_run_cmd,
        },
        'mapfile': map_filename,
        'logfile': log_filename,
        'max_steps': MAX_STEPS,
    }
    config_filename = 'config.json'
    with open(config_filename, 'w') as config_file:
        json.dump(config, config_file)

    game = arbiter.Game(config_filename)
    game.play()

    # TODO Parse log (log_filename) and output to some Match object
    # TODO Update some overall ranking


def db_session():
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    return Session()


if __name__ == '__main__':
    battle_on()
