from flask.ext.wtf import Form
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

from web.forms import BOTNAME_LENTGH


class BotForm(Form):
    botname = StringField('Name', validators=[DataRequired(),
                                              Length(*BOTNAME_LENTGH)])
    files = FileField('Files', validators=[DataRequired()])
    compile_cmd = StringField('Compile Command', validators=[Optional()])
    run_cmd = StringField('Run Command', validators=[DataRequired()])
    submit = SubmitField('Submit')
