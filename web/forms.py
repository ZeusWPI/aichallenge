from flask.ext.user.forms import RegisterForm
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired


class LoginForm(Form):
    nickname = StringField('name', validators=[DataRequired()])
    password = PasswordField('password')
    remember_me = BooleanField('remember_me', default=True)


class MyRegisterForm(RegisterForm):
    nickname = StringField('name', validators=[DataRequired()])
