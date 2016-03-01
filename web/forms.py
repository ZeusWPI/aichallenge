from flask.ext.user.forms import RegisterForm
from wtforms import StringField, BooleanField, PasswordField, Form
from wtforms.validators import DataRequired


class LoginForm(Form):
    nickname = StringField('name', validators=[DataRequired()])
    password = PasswordField('password')
    remember_me = BooleanField('remember_me', default=True)


class MyRegisterForm(RegisterForm):
    pass
