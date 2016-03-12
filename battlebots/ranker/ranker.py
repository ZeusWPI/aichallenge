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


def generate_graph(player_names):
    script = os.path.join(config.BASE_DIR, 'scripts', 'generate_graph.sh')
    #TODO: shadow names
    process = sp.Popen(script, stdout = sp.PIPE, in = sp.PIPE)
    for name in player_names:
        P.stdin.write("{}\n".format(name))
    P.stdin.close()
    return P.stdout


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

    # TODO: shadow names
    playermap = {
        'bot1': bot1.sandboxed_run_cmd,
        'bot2': bot2.sandboxed_run_cmd
        }

    # TODO: actually use a decent place for logfiles
    with (open('test.log', 'w') as logfile):
        game = arbiter.Game(playermap,
                            generate_graph(['bot1', 'bot2']),
                            MAX_STEPS,
                            logfile)
        game.play()
        # winner: game.winner()

    # TODO Update some overall ranking


def db_session():
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    return Session()


if __name__ == '__main__':
    battle_on()
