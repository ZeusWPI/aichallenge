import os

from flask import flash, redirect, render_template, abort, request
from flask.ext import login
from werkzeug import secure_filename

from battlebots import config
from battlebots.database import models, session
from battlebots.database.models import Bot, Match, User
from battlebots.web import app
from battlebots.web.forms.bots import BotForm


@app.route('/bots/', methods=('GET',))
@login.login_required
def bots():
    bots_ = session.query(Bot).filter_by(user=login.current_user)
    return render_template('bots/index.html', bots=bots_)


@app.route('/bots/new', methods=('GET', 'POST'))
@login.login_required
def new_bot():
    form = BotForm()
    if form.validate_on_submit():
        # TODO handle errors (like multiple bots with same name)
        add_bot(login.current_user, form)
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


@app.route('/bots/<user>/<botname>', methods=('GET',))
def bot_page(user, botname):
    user = session.query(User).filter_by(nickname=user).one()
    bot = session.query(Bot).filter_by(user=user, name=botname).one()
    return render_template('bots/bot.html', bot=bot)


@app.route('/matches/<matchid>')
def match_page(matchid):
    match = session.query(Match).filter_by(id=matchid).one()
    return render_template('bots/match.html', match=match)


def add_bot(user, form):
    # Save code to <BOT_CODE_DIR>/<user>/<botname>/<codename>
    files = request.files.getlist('files')
    parent = os.path.join(config.BOT_CODE_DIR, user.nickname, form.botname.data)
    os.makedirs(parent, exist_ok=True)

    #  TODO replace files
    for file in files:
        filename = secure_filename(file.filename)
        code_path = os.path.join(parent, filename)
        file.save(code_path)

    bot = Bot(
        user=user,
        name=form.botname.data,
        compile_cmd=form.compile_cmd.data,
        run_cmd=form.run_cmd.data)

    session.add(bot)
    session.commit()
