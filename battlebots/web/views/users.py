from flask import render_template, request, redirect, url_for, flash, abort
from flask.ext.login import login_required, login_user, logout_user

from battlebots.database import session
from battlebots.database import acces as db
from battlebots.database.models import User
from battlebots.web import app, lm
from battlebots.web.forms.users import LoginForm, RegisterForm


@app.route('/users/<user>')
def user_page(user):
    user = session.query(User).filter_by(nickname=user).one()
    return render_template('users/user.html', user=user)


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = session.query(User).filter_by(nickname=form.nickname.data).first()
        if user is None:
            abort(513)  # shouldn't happen

        if not login_user(user, remember=form.remember_me.data):
            flash('Failed to login.')
            return redirect(url_for('home'))

        url = request.args.get('next') or url_for('home')
        flash('Logged in succesfully!')
        return redirect(url)

    elif request.method == 'POST':
        flash('Failed to log in. Please check your credentials.')

    return render_template('users/login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logged out succesfully!')
    return redirect(url_for('home'))


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = RegisterForm()
    req = request
    if form.validate_on_submit():
        user = User(form.nickname.data, form.email.data, form.password.data)
        db.add(user)
        flash('Thanks for registering!')
        return redirect(url_for('login'))
    elif request.method == "POST":
        flash('Registering failed. Please supply all information', 'error')
        return render_template("users/register.html", form=form, error=form.errors)

    return render_template('users/register.html', form=form)


@lm.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login', next=request.base_url))


@lm.user_loader
def load_user(id):
    return session.query(User).filter(User.id == id).one()
