from flask import render_template, request, redirect, url_for, flash, abort, g, session
from flask_login import login_required, login_user, logout_user
from werkzeug.utils import secure_filename
from os import path
from markdown import Markdown

from web import app, db
from web.forms import LoginForm, MyRegisterForm
from web.models import User

@app.route('/home')
@app.route('/')
def home():
    return render_template("home.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        user = User.query.filter(User.nickname==form.nickname.data).first()

        if user is None:
            abort(513) # shouldn't happen
        login_user(user)
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


@app.route('/register', methods=['GET', 'POST'])
def register():
    kelly = MyRegisterForm()
    if request.method=="POST" and kelly.validate():
        print("validated")
        user = User(kelly.nickname.data, kelly.email.data,
                kelly.password.data)
        print(user)
        db.session.add(user)
        db.session.save()
        flash('Thanks for registering')
        return redirect(url_for('login'))
    elif request.method=="POST":
        print("Form", kelly.nickname)
        print("Non valid request")
    return render_template('register.html', form=kelly)


@app.route('/docs/<name>')
def docs(name):
    md = Markdown(extensions=['markdown.extensions.toc'])
    text = open(path.join('docs', secure_filename(name) + '.md')).read()
    html = md.convert(text)
    return render_template('doc.html', content=html, toc=md.toc)
