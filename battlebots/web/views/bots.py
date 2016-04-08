import os
import os.path as p
import shutil

from flask import flash, redirect, render_template, abort, request, url_for
from flask.ext import login
from sqlalchemy import desc
from werkzeug import secure_filename

from battlebots import config
from battlebots.database import session
from battlebots.database import access as db
from battlebots.database.models import Bot, Match, MatchParticipation, User
from battlebots.web import app
from battlebots.web.forms.bots import NewBotForm, UpdateBotForm
from battlebots.web.pagination_utils import paginate


@app.route('/bots/new', methods=('GET', 'POST'))
@login.login_required
def new_bot():
    form = NewBotForm()
    if form.validate_on_submit():
        # TODO handle errors (like multiple bots with same name)
        add_bot(login.current_user, form)
        flash('Uploaded bot "%s" succesfully!' % form.botname.data)
        return redirect(url_for('profile'))

    return render_template('bots/new.html', form=form)


@app.route('/bots/<username>/<botname>/update', methods=('GET', 'POST'))
@login.login_required
def update_bot(username, botname):
    if username != login.current_user.nickname:
        abort(400)  # Should not happen

    form = UpdateBotForm()
    user = session.query(User).filter_by(nickname=username).one_or_none()
    bot = session.query(Bot).filter_by(user=user, name=botname).one_or_none()

    if user is None:
        flash('User {} does not exist.')
        return redirect(url_for('users'))

    if bot is None:
        flash('{} does not exist or does not belong to {}'
              .format(botname, username))
        return redirect(url_for('profile'))

    if not form.compile_cmd.data and not form.run_cmd.data:
        form.compile_cmd.data = bot.compile_cmd
        form.run_cmd.data = bot.run_cmd

    if form.validate_on_submit():
        bot.compile_cmd = form.compile_cmd.data
        bot.run_cmd = form.run_cmd.data
        bot.compiled = False if bot.compile_cmd else bot.compiled

        files = request.files.getlist('files')
        parent = p.join(config.BOT_CODE_DIR, user.nickname, bot.name)
        make_files(files, parent)
        db.merge(bot)
        flash('Update bot "%s" succesfully!' % bot.name)
        return redirect(url_for('profile'))

    return render_template('bots/update.html', form=form)


@app.route('/bots/<username>/<botname>', methods=('POST',))
@login.login_required
def remove_bot(username, botname):
    if username != login.current_user.nickname:
        abort(400)  # Should not happen

    bot = (session.query(Bot)
           .filter_by(user=login.current_user, name=botname)
           .one_or_none())

    if bot is None:
        flash('{} does not exist or does not belong to {}'
              .format(botname, username))
        return redirect(url_for('profile'))

    db.remove_bot(bot)
    flash('Removed bot "%s" succesfully!' % botname)
    return redirect(url_for('profile'))


@app.route('/bots/<username>/<botname>', methods=('GET',))
def bot_page(username, botname):

    user = session.query(User).filter_by(nickname=username).one_or_none()
    if user is None:
        flash('User {} does not exist.')
        return redirect(url_for('users'))

    bot = session.query(Bot).filter_by(user=user, name=botname).one_or_none()
    if bot is None:
        flash('{} does not exist or does not belong to {}'
              .format(botname, username))
        return redirect(url_for('user_page', username=username))
    paginated_bot_participations_ = paginate(bot.participations.order_by(
        desc(MatchParticipation.match_id)
    ))

    return render_template(
        'bots/bot.html', bot=bot,
        paginated_bot_participations=paginated_bot_participations_)


@app.route('/matches/<matchid>')
def match_page(matchid):
    match = session.query(Match).filter_by(id=matchid).one_or_none()

    if match is None:
        flash('Match with id {} does not exist.'.format(matchid))
        return redirect(url_for('matches'))

    my_participations = [participation
                         for participation in match.participations
                         if participation.bot.user == login.current_user]
    return render_template('bots/match.html', match=match,
                           my_participations=my_participations)


def add_bot(user, form):
    # Save code to <BOT_CODE_DIR>/<user>/<botname>/<codename>
    files = request.files.getlist('files')
    parent = p.join(config.BOT_CODE_DIR, user.nickname, form.botname.data)

    make_files(files, parent)

    bot = Bot(
        user=user,
        name=form.botname.data,
        compile_cmd=form.compile_cmd.data,
        run_cmd=form.run_cmd.data,
        compiled=False if form.compile_cmd.data else True
    )

    db.add(bot)


def make_files(files, parent):
    if p.exists(parent):
        shutil.rmtree(parent)

    os.makedirs(parent)

    for file in files:
        filename = secure_filename(file.filename)
        code_path = os.path.join(parent, filename)
        file.save(code_path)
