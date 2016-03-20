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

GRAPH_WANDERLUST = 0
GRAPH_GENERATION_TIMEOUT = 20  # seconds
MAX_STEPS = 500


def generate_graph(player_names):
    script = os.path.join(config.BASE_DIR, 'scripts', 'generate_graph.sh')
    # TODO: shadow names
    input_ = b'\n'.join(name.encode('utf8') for name in player_names)
    try:
        process = sp.run([script, str(GRAPH_WANDERLUST)], input=input_,
                         stdout=sp.PIPE, stderr=sp.PIPE, check=True,
                         timeout=GRAPH_GENERATION_TIMEOUT)
    except sp.SubprocessError as error:
        logging.error('Graph generation failed.')
        logging.error(error)
        logging.error('Stdout was %s', error.stdout)
        logging.error('Stderr was %s', error.stderr)
        raise

    return [line.decode('utf8') for line in process.stdout.splitlines()]


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
