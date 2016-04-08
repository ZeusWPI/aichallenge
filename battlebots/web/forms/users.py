from flask.ext.wtf import Form
from wtforms import (StringField, BooleanField, PasswordField, SubmitField)
from wtforms.validators import DataRequired, Length, Email, EqualTo, NoneOf

from battlebots.arbiter import arbiter
from battlebots.database.models import User, PASSWORD_LENGTH, NICKNAME_LENGTH
from battlebots.web.validators import NonDuplicate, NoForwardSlashes
from battlebots.database import session


class LoginForm(Form):
    nickname = StringField('Name', validators=[DataRequired(), Length(*NICKNAME_LENGTH)])
    password = PasswordField('Password', validators=[DataRequired(), Length(*PASSWORD_LENGTH)])
    remember_me = BooleanField('Remember Me', default=True)
    submit = SubmitField('Sign In')

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return rv

        user = session.query(User).filter_by(nickname=self.nickname.data).one_or_none()
        if user is None:
            self.nickname.errors.append('User unknown.')
            return False

        check = user.check_password(self.password.data)
        if not check:
            self.nickname.errors.append('Incorrect password.')
            return False

        return True


class RegisterForm(Form):
    nickname = StringField(
        'Name',
        validators=[
            DataRequired(),
            Length(*NICKNAME_LENGTH),
            NonDuplicate(User, 'nickname'),
            NoneOf([arbiter.NO_PLAYER_NAME]),
            NoForwardSlashes()
        ])

    email = StringField(
        'E-mail',
        validators=[
            DataRequired(),
            Email(),
            NonDuplicate(User, 'email')
        ])

    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(*PASSWORD_LENGTH)])

    password_check = PasswordField(
        'Re-enter password',
        validators=[
            DataRequired(),
            EqualTo('password', message="Passwords must match.")
        ])

    submit = SubmitField('Sign up')
