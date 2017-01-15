from flask import render_template
from injector import inject

from app import app
from app.configurator import AppConfig


@app.route('/')
@app.route('/index')
@inject
def index(ac: AppConfig):
    return render_template('index.html', title='Home', user=ac.name)


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/peephole')
def peephole():
    return render_template('peephole.html', title='Peephole')


@app.route('/test')
def test():
    return render_template('test.html')

