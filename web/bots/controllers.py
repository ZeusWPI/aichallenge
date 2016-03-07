from flask import flash, redirect, render_template
from flask.ext import login
from web import app
from web.bots import models
from web.bots.models import Bot, User
from web.bots.forms import NewBotForm


@app.route('/bots/', methods=('GET',))
@login.login_required
def bots():
    bots = Bot.query.filter(User == login.current_user)
    return render_template('bots/index.html', bots=bots)


@app.route('/bots/new', methods=('GET', 'POST'))
@login.login_required
def new_bot():
    form = NewBotForm()
    if form.validate_on_submit():
        # TODO handle errors (like multiple bots with same name)
        models.add_bot(login.current_user, form)
        flash('Uploaded bot "%s" succesfully!' % form.name.data)
        return redirect('/bots')

    return render_template('bots/new.html', form=form)
