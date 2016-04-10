import logging
import gzip
import os.path
import re
import subprocess as sp
from itertools import dropwhile

from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as db
from sqlalchemy import desc
from sqlalchemy.orm import backref, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base


from battlebots import backports, config, sandbox
from battlebots.database import session
from battlebots.ranker.elo import DEFAULT_SCORE

Base = declarative_base()

NICKNAME_LENGTH = (1, 32)
PASSWORD_LENGTH = (1, 32)
BOTNAME_LENTGH = (1, 32)


class User(Base, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)

    nickname = db.Column(
        db.String(NICKNAME_LENGTH[1]),
        index=True,
        unique=True,
        nullable=False)

    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password = db.Column(db.String(120), index=True, nullable=False)

    bots = relationship(
        'Bot',
        back_populates='user',
        cascade='all, delete-orphan',
        passive_deletes=True)

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
        db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False)

    user = relationship(User, back_populates='bots')

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
        back_populates='bots',
        cascade='all')

    matches_won = relationship(
        'Match',
        back_populates='winner',
        cascade='all')

    compile_cmd = db.Column(db.String(200))
    run_cmd = db.Column(db.String(200), nullable=False)
    compiled = db.Column(db.Boolean, nullable=False, default=False)

    errors = association_proxy('participations', 'errors')

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
        """Return bot and owner name."""
        return '{bot} ({owner})'.format(bot=self.name,
                                        owner=self.user.nickname)

    @property
    def safe_full_name(self):
        """Return bot and owner name without spaces (but underscores)."""
        return re.sub(r'\s+', '_', self.full_name)

    def compile(self, timeout=20):
        """Return True if compilation succeeds, False otherwise."""

        if self.compiled:
            return True

        # TODO run async
        try:
            backports.sp_run(self.sandboxed_compile_cmd, check=True,
                             timeout=timeout, stdout=sp.PIPE, stderr=sp.PIPE)
            self.compiled = True
            return True
        except sp.SubprocessError as error:
            error = '{error}\nStdout: {stdout}\nStderr: {stderr}'.format(
                error=error,
                stdout=error.output.decode('utf8').rstrip(),
                stderr=error.stderr.decode('utf8').rstrip())
            logging.warning(error)
            self.compile_errors = error
            return False

    @property
    def sandboxed_compile_cmd(self):
        return sandbox.sandboxed(self.compile_cmd, self.code_path)

    @property
    def sandboxed_run_cmd(self):
        return sandbox.sandboxed(self.run_cmd, self.code_path)

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

    @property
    def rank(self):
        bots = enumerate(session.query(Bot).order_by(desc(Bot.score)).all())
        return next(dropwhile(lambda bot: bot[1] != self, bots))[0]


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

    errors = association_proxy('participations', 'errors')

    def __repr__(self):
        return '<Match on {start_time} between {bots}; {winner} won>'.format(
            start_time=self.start_time, bots=self.bots, winner=self.winner)

    @property
    def log_path(self):
        if not self.id:
            raise ValueError('ID was not set for this match. '
                             'Did you commit it to the database?')
        return os.path.join(config.MATCH_LOG_DIR, str(self.id) + '.gz')

    @property
    def log(self):
        try:
            with gzip.open(self.log_path, 'rb') as log_file:
                return log_file.read().decode('utf-8')
        except FileNotFoundError:
            logging.warning('File not found {}'.format(self.log_path))
            return None

    def save_log(self, content):
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        with gzip.open(self.log_path, 'wb') as logfile:
            logfile.write(content.encode('utf-8'))


class MatchParticipation(Base):
    __tablename__ = 'match_participation'

    match_id = db.Column(
        db.Integer,
        db.ForeignKey('match.id', ondelete='CASCADE'),
        primary_key=True)

    bot_id = db.Column(
        db.Integer,
        db.ForeignKey('bot.id', ondelete='CASCADE'),
        primary_key=True)

    match = relationship(
        Match,
        backref=backref('participations', cascade='all, delete-orphan',
                        passive_deletes=True))

    bot = relationship(
        Bot,
        backref=backref('participations', cascade='all, delete-orphan',
                        passive_deletes=True, lazy='dynamic'))

    errors = db.Column(db.Text)

    def __repr__(self):
        return ('<MatchParticipation of {bot} in {match}; errors: {errors}>'
                .format(bot=self.bot, match=self.match, errors=self.errors))
