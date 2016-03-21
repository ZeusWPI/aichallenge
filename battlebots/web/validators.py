from wtforms.validators import ValidationError

from battlebots.database import session
from battlebots.database.models import User


class NonDuplicate(object):
    def __init__(self, attribute):
        self.attribute = attribute

    def __call__(self, form, field):

        user = session.query(User).filter(
            getattr(User, self.attribute) == field.data
        ).first()

        if user is not None:
            raise ValidationError("{} already in use.".format(self.attribute))
