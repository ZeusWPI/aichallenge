import os.path
from werkzeug import secure_filename
from web import app, db
from web.models import User


class Bot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(User, backref='bots')
    name = db.Column(db.String(100), nullable=False, index=True, unique=True)
    code_path = db.Column(db.String(200), nullable=False)
    compile_cmd = db.Column(db.String(200))
    run_cmd = db.Column(db.String(200), nullable=False)
    # These two fields can be filled in by the compiler/ranker/arbiter
    compile_errors = db.Column(db.Text())
    run_errors = db.Column(db.Text())

    def __repr__(self):
        return '<Bot {} ({})>'.format(self.name, self.user.nickname)


def add_bot(user, form):
    # Save code to <BOT_CODE_DIR>/<user>/<botname>/<codename>
    code_filename = secure_filename(form.code.data.filename)
    code_path = os.path.join(app.config['BOT_CODE_DIR'], user.nickname,
                             form.name.data, code_filename)
    os.makedirs(os.path.dirname(code_path), exist_ok=False)
    form.code.data.save(code_path)

    bot = Bot(user=user, name=form.name.data, code_path=code_path,
              compile_cmd=form.compile_cmd.data, run_cmd=form.run_cmd.data)

    db.session.add(bot)
    db.session.commit()
