from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired


class LoginForm(Form):
    nickname = StringField('name', validators=[DataRequired()])
    password = PasswordField('password')
    remember_me = BooleanField('remember_me', default=True)
