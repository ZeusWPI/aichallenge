#!/usr/bin/env python

"""The fight is never over."""

import asyncio
from contextlib import ContextDecorator
from datetime import datetime
import logging
import os.path
import subprocess as sp
import tempfile
from time import sleep

import daemon
from lockfile.pidlockfile import PIDLockFile
from sqlalchemy.sql.expression import func

from battlebots import backports, config
from battlebots.arbiter import arbiter
from battlebots.database import access, session as db
from battlebots.database.models import Bot, Match, MatchParticipation

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
        process = backports.sp_run([script, str(GRAPH_WANDERLUST)],
                                   input=input_, stdout=sp.PIPE,
                                   stderr=sp.PIPE, check=True,
                                   timeout=GRAPH_GENERATION_TIMEOUT)
    except sp.SubprocessError as error:
        logging.error('Graph generation failed.')
        logging.error(error)
        logging.error('Stdout was %s', error.output.decode('utf8'))
        logging.error('Stderr was %s', error.stderr.decode('utf8'))
        raise

    return [line.decode('utf8') for line in process.stdout.splitlines()]


def find_participants(n=2):
    bots = list(db.query(Bot).order_by(func.random()).limit(n))

    if len(bots) != n:
        raise LookupError('Not enough bots found in database')

    logging.info('Letting %s fight', bots)
    return bots


def battle(loop):
    bots = find_participants()
    bot_map = {bot.safe_full_name: bot for bot in bots}

    logging.info('Starting compilation')
    # TODO compile async
    compilation_success = all(bot.compile() for bot in bots)
    if not compilation_success:
        # Save errors on bots
        access.add_all(bots)
        logging.warning('Compilation failed')
        return
    logging.info('Compilation done')

    logging.info('Starting graph generation')
    graph = generate_graph(bot_map.keys())
    logging.info('Graph generated: %s', ' | '.join(graph))

    with tempfile.TemporaryFile('w+') as tmp_logfile:
        cmd_map = {name: bot.sandboxed_run_cmd
                   for name, bot in bot_map.items()}
        game = arbiter.Game(cmd_map, graph, MAX_STEPS, tmp_logfile)
        player_map = game.players.copy()

        logging.info('Starting match')
        with Timed() as timings:
            loop.run_until_complete(game.play_async())
        logging.info('Stopping match')

        winner = game.winner()
        if winner:
            winner = bot_map.get(winner.name)
        logging.info('{} won'.format(winner) if winner else 'Draw')

        # Save match outcome to database
        match = Match(winner=winner, start_time=timings.start_time,
                      end_time=timings.end_time)
        for name, bot in bot_map.items():
            warnings = '\n'.join(player_map[name].warnings)
            participation = MatchParticipation(bot=bot, errors=warnings)
            match.participations.append(participation)

        try:
            # Saves match object, but also adds an ID so we know where to save
            # the log of the match to.
            db.add(match)
            db.commit()

            # Store the log file to match.log_path
            tmp_logfile.seek(0)
            match.save_log(tmp_logfile.read())
        except:
            logging.exception("Database had to do a rollback.")
            db.rollback()
            raise


def battle_loop():
    loop = asyncio.get_event_loop()
    try:
        while True:
            try:
                battle(loop)
                sleep(10)
            except Exception:
                logging.exception('Ranker encountered a fatal error')
                # Keep trying after a while
                sleep(300)
    except KeyboardInterrupt:
        logging.info('Stopping ranker')
    finally:
        loop.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--daemonize', action='store_true',
                        help='whether to run the ranker as a daemon')

    args = parser.parse_args()

    if args.daemonize:
        log_file = open(config.RANKER_LOG, 'a+')
        pid_file = PIDLockFile(os.path.join(config.REPO_ROOT, 'ranker.pid'))
        daemon_context = daemon.DaemonContext(
            stderr=log_file,
            pidfile=pid_file,
            working_directory=os.environ['HOME'])

        with daemon_context:
            battle_loop()
    else:
        battle_loop()


if __name__ == '__main__':
    main()
