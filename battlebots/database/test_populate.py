import datetime as d

from battlebots.database import scoped_session
from battlebots.database.models import User, Bot, Match, MatchParticipation

user1 = User('tester1', 'test1@mail.com', 'test_pw_1')
user2 = User('tester2', 'test2@mail.com', 'test_pw_2')

bot1 = Bot(name='bot1', user=user1, compile_cmd='', run_cmd='', score=1000)
bot2 = Bot(name='bot2', user=user2, compile_cmd='', run_cmd='', score=1100)

match1 = Match(winner=bot1, start_time=d.datetime.today(), end_time=d.datetime.today())

mp1 = MatchParticipation(match=match1, bot=bot1, errors="test error 1")
mp2 = MatchParticipation(match=match1, bot=bot2)


l = [user1, user2, bot1, bot1, match1]

with scoped_session() as db:
    for x in l:
        db.add(x)
