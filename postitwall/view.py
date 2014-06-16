# Python 2/3 compatibility
from __future__ import division, absolute_import, print_function, unicode_literals

import markdown

from flask import Flask, render_template, redirect
from jinja2 import evalcontextfilter, Markup

from board import Board
import settings


app = Flask(__name__)


@app.template_filter()
def md2html(value):
    return Markup(markdown.markdown(value, extensions=['urlize']))


@app.route("/")
def index():
    board_lst = [Board(name, filters) for name, filters in settings.BOARDS]
    return render_template("index.html", board_lst=board_lst)


@app.route("/favicon.ico")
def favicon():
    return redirect("/static/favicon.ico", 301)
