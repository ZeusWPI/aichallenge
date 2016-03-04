from flask.ext.wtf import Form
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class NewBotForm(Form):
    name = StringField('Bot name', validators=[DataRequired()])
    code = FileField('Code', validators=[DataRequired()])
    compile_cmd = StringField('Compile command')
    run_cmd = StringField('Run command', validators=[DataRequired()])
    submit = SubmitField('Upload bot')
