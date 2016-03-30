from wtforms.validators import ValidationError

from battlebots.database import session
from battlebots.database.models import User

MAX_FILE_AMOUNT = 50


class NonDuplicate(object):
    def __init__(self, attribute):
        self.attribute = attribute

    def __call__(self, _, field):

        user = session.query(User).filter(
            getattr(User, self.attribute) == field.data
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
