from flask.ext.wtf import Form
from wtforms import (StringField, BooleanField, PasswordField, SubmitField, FileField,
                     ValidationError)
from wtforms.validators import DataRequired, Length, Email, Optional, EqualTo
from web.models import User

NICKNAME_LENGTH = (1, 32)
PASSWORD_LENGTH = (1, 32)
BOTNAME_LENTGH = (1, 32)


class LoginForm(Form):
    nickname = StringField('Name', validators=[DataRequired(), Length(*NICKNAME_LENGTH)])
    password = PasswordField('Password', validators=[DataRequired(), Length(*PASSWORD_LENGTH)])
    remember_me = BooleanField('Remember Me', default=True)
    submit = SubmitField('Sign In')

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return rv

        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user is None:
            self.nickname.errors.append('User unknown.')
            return False

        check = user.check_password(self.password.data)
        if not check:
            self.nickname.errors.append('Incorrect password.')
            return False

        return True


class RegisterForm(Form):
    nickname = StringField('Name', validators=[DataRequired(), Length(*NICKNAME_LENGTH)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(*PASSWORD_LENGTH)])
    password_check = PasswordField('Re-enter password',
                                   validators=[DataRequired(), EqualTo('password', message="Passwords must match.")])
    submit = SubmitField('Sign up')
