from web import db, lm
from flask.ext.login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, \
     check_password_hash


class User(db.Model, UserMixin):
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


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))
