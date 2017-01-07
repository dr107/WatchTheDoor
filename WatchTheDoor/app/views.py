from flask import render_template
from injector import inject

from app import app
from app.configurator import AppConfig


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home', user='Dan & Nelson')


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/peephole')
@inject
def peephole(ac: AppConfig):
    return render_template('peephole.html', title='Peephole', host=ac.host)


@app.route('/test')
def test():
    return render_template('test.html')

