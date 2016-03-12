import logging
import os.path
import shutil

from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request
from werkzeug import secure_filename
import sqlalchemy as db
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from battlebots import config, Session

Base = declarative_base()

class User(Base, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(120), index=True)

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


@contextlib.contextmanager
def in_dir(directory):
    prev_dir = os.getcwd()
    os.chdir(directory)
    yield
    os.chdir(prev_dir)

class Bot(Base):
    __tablename__ = 'bot'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship(User, backref='bots')
    name = db.Column(db.String(100), nullable=False, index=True, unique=True)
    compile_cmd = db.Column(db.String(200))
    run_cmd = db.Column(db.String(200), nullable=False)
    # These two fields can be filled in by the compiler/ranker/arbiter
    compile_errors = db.Column(db.Text())
    run_errors = db.Column(db.Text())

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


def add_bot(user, form):
    # Save code to <BOT_CODE_DIR>/<user>/<botname>/<codename>
    files = request.files.getlist('files')
    parent = os.path.join(config.BOT_CODE_DIR, user.nickname,
                          form.botname.data)
    os.makedirs(parent, exist_ok=True)

    #  TODO replace files
    for file in files:
        filename = secure_filename(file.filename)
        code_path = os.path.join(parent, filename)
        file.save(code_path)

    bot = Bot(user=user, name=form.botname.data,
              compile_cmd=form.compile_cmd.data, run_cmd=form.run_cmd.data)

    session.add(bot)
    session.commit()


def remove_bot(user, botname):
    code_dir = os.path.join(app.config['BOT_CODE_DIR'], user.nickname, botname)
    try:
        shutil.rmtree(code_dir)
    except FileNotFoundError:
        # Don't crash if for some reason this dir doesn't exist anymore
        logging.warn('Code dir of bot %s:%s not found (%s)'
                     % (user.nickname, botname, code_dir))
        pass

    bot = Bot.query.filter_by(user=user, name=botname).one()
    session.delete(bot)
    session.commit()


