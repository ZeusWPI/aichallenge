from wtforms.validators import ValidationError

from battlebots.database import scoped_session
from battlebots.database.models import User

MAX_FILE_AMOUNT = 50


class NonDuplicate(object):
    def __init__(self, class_, attribute):
        self.class_ = class_
        self.attribute = attribute

    def __call__(self, _, field):

        with scoped_session() as db:
            user = db.query(self.class_).filter(
                getattr(self.class_, self.attribute) == field.data
            ).first()

        if user is not None:
            raise ValidationError("{} already in use.".format(self.attribute))


class MaxFileAmount(object):
    def __call__(self, form, _):
        files = form.files.raw_data
        if len(files) > MAX_FILE_AMOUNT:
            raise ValidationError(
                'More than {} files, seriously?'
                ' Cut that down baby.'.format(MAX_FILE_AMOUNT)
            )
