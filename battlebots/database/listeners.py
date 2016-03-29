from sqlalchemy import event

from battlebots.database.models import Bot


@event.listens_for(Bot.matches, 'append')
def new_match(bot, _):
    bot.score = bot.win_percentage
