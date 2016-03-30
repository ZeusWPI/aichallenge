from flask.ext.wtf import Form
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

from battlebots.database.models import BOTNAME_LENTGH
from battlebots.web.validators import MaxFileAmount


class NewBotForm(Form):
    botname = StringField('Name', validators=[DataRequired(),
                                              Length(*BOTNAME_LENTGH)])
    files = FileField('Files', validators=[DataRequired(), MaxFileAmount()])
    compile_cmd = StringField('Compile Command', validators=[Optional()])
    run_cmd = StringField('Run Command', validators=[DataRequired()])
    submit = SubmitField('Submit')


class UpdateBotForm(Form):
    files = FileField('Files', validators=[DataRequired(), MaxFileAmount()])
    compile_cmd = StringField('Compile Command', validators=[Optional()])
    run_cmd = StringField('Run Command', validators=[DataRequired()])
    submit = SubmitField('Update')
