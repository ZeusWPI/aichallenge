#from sqlalchemy import event
#
#from battlebots.database import Session, scoped_session
#from battlebots.database.models import MatchParticipation
#from battlebots.ranker.elo import elo_diff
#
#
#@event.listens_for(Session, 'before_commit')
#def update_bot_ratings(Session):
#    # If anyone finds a better way to update the ratings, please do
#
#    with scoped_session() as db:
#        participations = [obj for obj in db.new
#                        if isinstance(obj, MatchParticipation)]
#
#    if not participations:
#        return
#
#    match = participations[0].match
#    assert all(match == p.match for p in participations[1:])
#
#    participants = [participation.bot for participation in participations]
#    for participant in participants:
#        change = elo_diff(participant, match.winner, participants)
#        participant.score += change
