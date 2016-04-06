from flask import render_template
from sqlalchemy import desc

from battlebots.web import app
from battlebots.web.pagination_utils import paginate
from battlebots.database import session
from battlebots.database.models import Bot, Match


@app.route('/home')
@app.route('/')
def home():
    return render_template('home.md')


@app.route('/ranking')
def ranking():
    bots = session.query(Bot).order_by(desc(Bot.score))
    ranked_bots = enumerate(bots)
    return render_template('ranking.html', bots=ranked_bots)


@app.route('/matches/')
def matches():
    matches_ = session.query(Match).order_by(desc(Match.id))
    paginated_matches_ = paginate(matches_)

    return render_template('matches.html', paginated_matches=paginated_matches_)


@app.route('/rules')
def rules():
    return render_template('rules.md')
