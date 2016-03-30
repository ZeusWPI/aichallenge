from statistics import mean

from sqlalchemy import event

from battlebots.database.models import Bot, K_FACTOR

WIN_RESULT = 1
LOSE_RESULT = 0
DRAW_RESULT = 0.5


@event.listens_for(Bot.matches, 'append')
def new_match(bot, match, _):
    result = get_result(bot, match)
    opponents = match.participants - bot
    bot.score += change_amount(bot, opponents, result)


def get_result(bot, match):
    if not any(bot == match.winner for bot in match.participants):
        return DRAW_RESULT

    return WIN_RESULT if match.winner == bot else LOSE_RESULT


def expected_result(a, b):
    return 10 ** (a / 400) / (10 ** (a / 400) + 10 ** (b / 400))


def change_amount(bot, opponents, outcome):
    change = lambda a, b: K_FACTOR * (outcome - expected_result(a, b))
    return mean(change(bot.score, op.score) for op in opponents)
