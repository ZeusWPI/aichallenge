from statistics import mean

from sqlalchemy import event

from battlebots.database.models import Bot, K_FACTOR


@event.listens_for(Bot.matches, 'append')
def new_match(bot, match, _):
    result = int(match.winner == bot)
    opponents = match.participants - bot
    bot.score += change_amount(bot, opponents, result)


def expected_result(a, b):
    return 10 ** (a / 400) / (10 ** (a / 400) + 10 ** (b / 400))


def change_amount(bot, opponents, outcome):
    change = lambda a, b: K_FACTOR * (outcome - expected_result(a, b))
    return mean(change(bot.score, op.score) for op in opponents)
