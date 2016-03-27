#!/usr/bin/env python
from contextlib import ContextDecorator
from datetime import datetime
import logging
import os.path
import subprocess as sp
import tempfile

from sqlalchemy.sql.expression import func

from battlebots.database.models import Bot, Match, MatchParticipation
from battlebots.database import session as db
from battlebots import config
from battlebots.arbiter import arbiter

GRAPH_WANDERLUST = 0
GRAPH_GENERATION_TIMEOUT = 20  # seconds
MAX_STEPS = 500


class Timed(ContextDecorator):
    def __enter__(self):
        self.start_time = datetime.now()
        return self

    def __exit__(self, *exc):
        self.end_time = datetime.now()


def generate_graph(player_names):
    script = os.path.join(config.BASE_DIR, 'scripts', 'generate_graph.sh')
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


def battle():
    bot1 = db.query(Bot).order_by(func.random()).first()
    bot2 = db.query(Bot).order_by(func.random()).first()
    if not bot1 or not bot2:
        logging.error('No bots found in database')
        return
    logging.info('Letting %r and %r fight', bot1, bot2)

    logging.info('Starting compilation')
    # TODO compile async
    compilation_success = all(bot.compile() for bot in (bot1, bot2))
    if not compilation_success:
        # Save errors on bots
        db.add_all((bot1, bot2))
        db.commit()
        logging.warn('Compilation failed')
        return
    logging.info('Compilation done')

    logging.info('Starting graph generation')
    graph = generate_graph([bot1.full_name, bot2.full_name])
    logging.info('Graph generated: %s', ' | '.join(graph))

    bot2_name = bot2.full_name + ('²' if bot1 == bot2 else '')
    playermap = {
        bot1.full_name: bot1.sandboxed_run_cmd,
        bot2_name: bot2.sandboxed_run_cmd
    }

    with tempfile.TemporaryFile('w+') as tmp_logfile:
        game = arbiter.Game(playermap, graph, MAX_STEPS, tmp_logfile)
        logging.info('Starting match')
        with Timed() as timings:
            game.play()
        logging.info('Stopping match')

        winner = game.winner()
        if winner:
            winner = bot1 if winner.name == bot1.full_name else bot2
        logging.info('{} won'.format(winner) if winner else 'Draw')

        # Save match outcome to database
        match = Match(winner=winner, start_time=timings.start_time,
                      end_time=timings.end_time)
        # TODO extract errors from arbiter and add them here
        for bot in {bot1, bot2}:
            match.participations.append(MatchParticipation(bot=bot, errors=''))
        db.add(match)
        db.commit()

        # Store the log file to match.log_path
        tmp_logfile.seek(0)
        match.save_log(tmp_logfile.read())


if __name__ == '__main__':
    try:
        battle()
    except KeyboardInterrupt:
        logging.info('Stopping ranker')
