import os.path
import re
import subprocess as sp
from contextlib import contextmanager

from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as db
from sqlalchemy.orm import backref, relationship
from sqlalchemy.ext.declarative import declarative_base


from battlebots import config
from battlebots.database import engine
from battlebots.ranker.elo import DEFAULT_SCORE

Base = declarative_base()

NICKNAME_LENGTH = (1, 32)
PASSWORD_LENGTH = (1, 32)
BOTNAME_LENTGH = (1, 32)


class User(Base, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(NICKNAME_LENGTH[1]), index=True,
                         unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password = db.Column(db.String(120), index=True, nullable=False)

    def __repr__(self):
        return '<User {}>'.format(self.nickname)

    def __init__(self, nickname, email, password):
        self.nickname = nickname
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Bot(Base):
    __tablename__ = 'bot'
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False)

    user = relationship(User, backref='bots')

    name = db.Column(
        db.String(BOTNAME_LENTGH[1]),
        nullable=False,
        index=True,
        unique=True)

    score = db.Column(
        db.Integer,
        nullable=False,
        default=DEFAULT_SCORE,
        index=True)

    matches = relationship(
        'Match',
        secondary='match_participation',
        back_populates='bots')

    matches_won = relationship('Match', back_populates='winner')

    compile_cmd = db.Column(db.String(200))
    run_cmd = db.Column(db.String(200), nullable=False)
    compiled = db.Column(db.Boolean, nullable=False, default=False)

    # These two fields can be filled in by the compiler/ranker/arbiter
    compile_errors = db.Column(db.Text)
    run_errors = db.Column(db.Text)

    # TODO make run_errors an association proxy to errors of MatchParticipation
    # objects

    def __repr__(self):
        return '<Bot {}>'.format(self.full_name)

    @property
    def code_path(self):
        return os.path.join(config.BOT_CODE_DIR, self.user.nickname, self.name)

    @property
    def full_name(self):
        """Return bot and owner name without spaces (but underscores)."""
        full_name_with_spaces = '{bot} ({owner})'.format(
            bot=self.name, owner=self.user.nickname)
        return re.sub(r'\s+', '_', full_name_with_spaces)

    def compile(self, timeout=20):
        """Return True if compilation succeeds, False otherwise."""

        if self.compiled:
            return True

        # TODO run in sandbox & async
        with _in_dir(self.code_path):
            try:
                sp.run(self.compile_cmd, stdout=sp.PIPE, stderr=sp.PIPE,
                       shell=True, check=True, timeout=timeout)
                self.compiled = True
                return True
            except sp.SubprocessError as error:
                self.compile_errors = str(error)
                self.compile_errors += 'STDOUT:\n' + error.stdout
                self.compile_errors += 'STDERR:\n' + error.stderr
                return False

    @property
    def sandboxed_run_cmd(self):
        # TODO
        return 'cd "%s" && %s' % (self.code_path, self.run_cmd)

    @property
    def win_percentage(self):
        all_matches = len(self.matches)
        if all_matches is not 0:
            won_matches = len(self.matches_won)
            return round(won_matches / all_matches * 100, 2)
        else:
            return None

    @property
    def loss_percentage(self):
        return 100 - self.win_percentage
    

class Match(Base):
    __tablename__ = 'match'
    id = db.Column(db.Integer, primary_key=True)

    bots = relationship(
        Bot,
        secondary='match_participation',
        back_populates='matches')

    winner_id = db.Column(db.Integer, db.ForeignKey('bot.id'))
    winner = relationship(Bot, back_populates='matches_won')
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<Match between {bots}; {winner} won; log: {logfile}>'.format(
            bots=self.bots, winner=self.winner, logfile=self.logfile)

    @property
    def log_path(self):
        return os.path.join(config.MATCH_LOG_DIR, str(self.id))

    def save_log(self, content):
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        with open(self.log_path, 'w') as logfile:
            logfile.write(content)


class MatchParticipation(Base):
    __tablename__ = 'match_participation'

    match_id = db.Column(
        db.Integer,
        db.ForeignKey('match.id'),
        primary_key=True)

    bot_id = db.Column(
        db.Integer,
        db.ForeignKey('bot.id'),
        primary_key=True)

    match = relationship(
        Match,
        backref=backref('participations', cascade='all, delete-orphan'))

    bot = relationship(
        Bot,
        backref=backref('participations', cascade='all, delete-orphan'))

    errors = db.Column(db.Text)

    def __repr__(self):
        return ('<MatchParticipation of {bot} in {match}; errors: {errors}>'
                .format(bot=self.bot, match=self.match, errors=self.errors))


@contextmanager
def _in_dir(directory):
    prev_dir = os.getcwd()
    os.chdir(directory)
    yield
    os.chdir(prev_dir)


Base.metadata.create_all(engine)
