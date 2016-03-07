from flask import flash, redirect, render_template, abort
from flask.ext import login
from web import app
from web.bots import models
from web.bots.models import Bot
from web.bots.forms import BotForm


@app.route('/bots/', methods=('GET',))
@login.login_required
def bots():
    bots = Bot.query.filter_by(user=login.current_user)
    return render_template('bots/index.html', bots=bots)


@app.route('/bots/new', methods=('GET', 'POST'))
@login.login_required
def new_bot():
    form = BotForm()
    if form.validate_on_submit():
        # TODO handle errors (like multiple bots with same name)
        models.add_bot(login.current_user, form)
        flash('Uploaded bot "%s" succesfully!' % form.botname.data)
        return redirect('/bots')

    return render_template('bots/new.html', form=form)


@app.route('/bots/<user>/<botname>', methods=('POST',))
@login.login_required
def remove_bot(user, botname):
    if user != login.current_user.nickname:
        abort(400)  # Should not happen
    models.remove_bot(login.current_user, botname)
    flash('Removed bot "%s" succesfully!' % botname)
    return redirect('/bots')
