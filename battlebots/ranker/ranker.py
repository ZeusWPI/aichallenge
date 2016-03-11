#!/usr/bin/env python
import contextlib
import json
import logging
import os.path
import subprocess as sp

from sqlalchemy import create_engine, Column, Integer, ForeignKey, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from battlebots import config
from battlebots.arbiter import arbiter

MAX_STEPS = 500
Base = declarative_base()


# TODO remove ORM duplication
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    nickname = Column(String(64), index=True, unique=True)
    email = Column(String(120), index=True, unique=True)
    password = Column(String(120), index=True)


class Bot(Base):
    __tablename__ = 'bot'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref='bots')
    name = Column(String(100), nullable=False, index=True, unique=True)
    compile_cmd = Column(String(200))
    run_cmd = Column(String(200), nullable=False)
    # These two fields can be filled in by the compiler/ranker/arbiter
    compile_errors = Column(Text())
    run_errors = Column(Text())

    def __repr__(self):
        return '<Bot {} ({})>'.format(self.name, self.user.nickname)

    @property
    def code_path(self):
        return os.path.join(config.BOT_CODE_DIR, self.user.nickname, self.name)

    @property
    def full_name(self):
        return '%s (%s)' % (self.name, self.user.nickname)

    def compile(self):
        """Return True if compilation succeeds, False otherwise."""

        # TODO run in sandbox & async
        with in_dir(self.code_path):
            process = sp.Popen(self.compile_cmd, stdout=sp.PIPE,
                               stderr=sp.PIPE, shell=True)
            process.wait(timeout=20)

            if process.returncode == 0:
                return True

            self.compile_errors = ('Compilation exited with error code %d.\n\n'
                                   % process.returncode)
            self.compile_errors += 'STDOUT:\n' + process.stdout.read()
            self.compile_errors += 'STDERR:\n' + process.stderr.read()
            return False

    @property
    def sandboxed_run_cmd(self):
        # TODO
        return 'cd "%s" && %s' % (self.code_path, self.run_cmd)


@contextlib.contextmanager
def in_dir(directory):
    prev_dir = os.getcwd()
    os.chdir(directory)
    yield
    os.chdir(prev_dir)


def battle_on():
    db = db_session()

    # TODO choose two random bots
    bot1 = bot2 = db.query(Bot).first()

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
