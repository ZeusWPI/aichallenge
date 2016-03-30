from sqlalchemy import event

from battlebots.database.models import Bot
from battlebots.ranker.elo import elo_diff


@event.listens_for(Bot.matches, 'append')
def new_match(bot, match, _):
    change = elo_diff(bot, match)
    bot.score += change

