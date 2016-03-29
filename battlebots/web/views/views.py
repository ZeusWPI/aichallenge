from flask import render_template
from flask.ext.login import current_user


from battlebots.web import app, lm
from battlebots.database import session
from battlebots.database.models import Bot


@app.route('/home')
@app.route('/')
def home():
    return render_template('home.md')


@app.route('/ranking')
def ranking():
    bots = session.query(Bot).order_by(Bot.score).filter_by(user=current_user)
    ranked_bots = enumerate(bots)
    return render_template('ranking.html', bots=ranked_bots)


@app.route('/rules')
def rules():
    return render_template('rules.md')
