from flask.ext.wtf import Form
from wtforms import (StringField, BooleanField, PasswordField, SubmitField,
                     ValidationError)
from wtforms.validators import DataRequired
from web.models import User


class LoginForm(Form):
    nickname = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
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
    nickname = StringField('Name', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_check = PasswordField('Re-enter password',
                                   validators=[DataRequired()])
    submit = SubmitField('Sign up')

    def validate_password_check(self, password_check):
        password = self.password.data
        if password != password_check.data:
            raise ValidationError("Passwords are not the same.")
