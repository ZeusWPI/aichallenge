from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from os import path
from markdown import Markdown

app = Flask(__name__)


@app.route('/home')
@app.route('/')
def home():
    return render_template("home.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/docs/<name>')
def docs(name):
    md = Markdown(extensions=['markdown.extensions.toc'])
    text = open(path.join('docs', secure_filename(name) + '.md')).read()
    html = md.convert(text)
    return render_template('doc.html', content=html, toc=md.toc)


if __name__ == '__main__':
    app.run(debug=True)
