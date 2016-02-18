from flask import Flask, render_template
from werkzeug.utils import secure_filename
from os import path
from markdown import Markdown

app = Flask(__name__)

@app.route('/')
def landing_page():
    return docs('teaser')

@app.route('/docs/<name>')
def docs(name):
    md = Markdown(extensions=['markdown.extensions.toc'])
    text = open(path.join('docs', secure_filename(name) + '.md')).read()
    html = md.convert(text)
    return render_template('doc.html', content=html, toc=md.toc)

if __name__ == '__main__':
    app.run()
