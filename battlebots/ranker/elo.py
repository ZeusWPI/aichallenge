from statistics import mean

DEFAULT_SCORE = 1000
K_FACTOR = 10

WIN_RESULT = 1
LOSE_RESULT = 0
DRAW_RESULT = 0.5


def elo_diff(bot, winner, participants):
    result = get_result(bot, winner, participants)
    opponents = set(participants) - {bot}
    return change_amount(bot, opponents, result)


def get_result(bot, winner, participants):
    if not any(bot == winner for bot in participants):
        return DRAW_RESULT

    return WIN_RESULT if winner == bot else LOSE_RESULT


def expected_result(a, b):
    return 10 ** (a / 400) / (10 ** (a / 400) + 10 ** (b / 400))


def change_amount(bot, opponents, outcome):
    return mean(K_FACTOR *
                (outcome - expected_result(bot.score, opponent.score))
                for opponent in opponents)
