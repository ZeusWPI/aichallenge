from flask.ext.wtf import Form
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NoneOf

from battlebots.arbiter import arbiter
from battlebots.database.models import BOTNAME_LENTGH, Bot
from battlebots.web.validators import \
    (MaxFileAmount, NonDuplicate, NoForwardSlashes)


class NewBotForm(Form):
    botname = StringField(
        'Name', validators=[
            DataRequired(),
            Length(*BOTNAME_LENTGH),
            NonDuplicate(Bot, 'name'),
            NoneOf([arbiter.NO_PLAYER_NAME]),
            NoForwardSlashes()
        ])

    files = FileField('Files', validators=[DataRequired(), MaxFileAmount()])
    compile_cmd = StringField('Compile Command', validators=[Optional()])
    run_cmd = StringField('Run Command', validators=[DataRequired()])
    submit = SubmitField('Submit')


class UpdateBotForm(Form):
    files = FileField('Files', validators=[DataRequired(), MaxFileAmount()])
    compile_cmd = StringField('Compile Command', validators=[Optional()])
    run_cmd = StringField('Run Command', validators=[DataRequired()])
    submit = SubmitField('Update')
