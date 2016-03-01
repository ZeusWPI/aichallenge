from flask import render_template, request, redirect, url_for, flash, abort, g, session
from flask_login import login_required, login_user, logout_user, LoginManager
from werkzeug.utils import secure_filename
from os import path
from markdown import Markdown

from web import app
from web.forms import LoginForm
from web.models import User


lm = LoginManager()
lm.init_app(app)


@app.route('/home')
@app.route('/')
def home():
    return render_template("home.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        flash('Logged in successfully.')

        _next = request.args.get('next')
        if _next == '':
            return abort(400)

        return redirect(_next or url_for('home'))
    return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('home.html')


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/register')
def register():
    pass


@app.route('/docs/<name>')
def docs(name):
    md = Markdown(extensions=['markdown.extensions.toc'])
    text = open(path.join('docs', secure_filename(name) + '.md')).read()
    html = md.convert(text)
    return render_template('doc.html', content=html, toc=md.toc)
