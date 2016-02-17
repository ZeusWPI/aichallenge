from flask import Flask, render_template
from markdown import Markdown

app = Flask(__name__)

@app.route('/')
def landing_page():
    md = Markdown(extensions=['markdown.extensions.toc'])
    with open('content.md', 'r') as f:
        text = f.read()
    html = md.convert(text)
    return render_template('landing.html', content=html, toc=md.toc)

if __name__ == '__main__':
    app.run(debug=True)
