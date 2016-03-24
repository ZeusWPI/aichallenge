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
    bots = session.query(Bot).filter_by(user=current_user)
    return render_template('ranking.html', bots=bots)


@app.route('/rules')
def rules():
    return render_template('rules.md')
