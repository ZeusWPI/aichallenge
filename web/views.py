import os.path

from flask import render_template, request, redirect, url_for, flash, abort
from flask.ext.login import login_required, login_user, logout_user
from markdown import Markdown

from web import app, db
from web.forms import LoginForm, RegisterForm
from web.models import User


@app.route('/home')
@app.route('/')
def home():
    return render_markdown('home')


@app.route('/rules')
def rules():
    return render_markdown('rules')


@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.nickname == form.nickname.data).first()
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

    return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logged out succesfully!')
    return redirect(url_for('home'))


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(form.nickname.data, form.email.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering!')
        return redirect(url_for('login'))
    elif request.method == "POST":
        flash('Registering failed. Please supply all information', 'error')

    return render_template('register.html', form=form)


def markdown_to_html(name):
    md = Markdown()
    text = open(os.path.join('docs', name + '.md')).read()
    return md.convert(text)


def render_markdown(name):
    content = markdown_to_html(name)
    return render_template('markdown.html', name=name, content=content)
