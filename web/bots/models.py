import os.path
import shutil
import logging

from flask import request
from werkzeug import secure_filename

from web import app, db
from web.models import User


class Bot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(User, backref='bots')
    name = db.Column(db.String(100), nullable=False, index=True, unique=True)
    compile_cmd = db.Column(db.String(200))
    run_cmd = db.Column(db.String(200), nullable=False)
    # These two fields can be filled in by the compiler/ranker/arbiter
    compile_errors = db.Column(db.Text())
    run_errors = db.Column(db.Text())

    def __repr__(self):
        return '<Bot {} ({})>'.format(self.name, self.user.nickname)


def add_bot(user, form):
    # Save code to <BOT_CODE_DIR>/<user>/<botname>/<codename>
    files = request.files.getlist('files')
    parent = os.path.join(app.config['BOT_CODE_DIR'], user.nickname,
                          form.botname.data)
    os.makedirs(parent, exist_ok=True)

    #  TODO replace files
    for file in files:
        filename = secure_filename(file.filename)
        code_path = os.path.join(parent, filename)
        file.save(code_path)

    bot = Bot(user=user, name=form.botname.data,
              compile_cmd=form.compile_cmd.data, run_cmd=form.run_cmd.data)

    db.session.add(bot)
    db.session.commit()


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
    db.session.delete(bot)
    db.session.commit()
