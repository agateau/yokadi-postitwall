# Python 2/3 compatibility
from __future__ import division, absolute_import, print_function, unicode_literals

import itertools

import markdown

from flask import Flask, render_template, redirect
from jinja2 import Markup

from board import Board
import settings


app = Flask(__name__)


@app.template_filter()
def md2html(value):
    return Markup(markdown.markdown(value, extensions=['urlize']))


def sort_and_group(lst, key):
    lst = sorted(lst, key=key)
    return itertools.groupby(lst, key)


def create_board_info(board):
    class ProjectInfo(object):
        def __init__(self, name, tasks):
            self.name = name
            tasks = sort_and_group(tasks, key=lambda x: x.status)
            self.tasks = dict((k, list(v)) for k, v in tasks)

    class BoardInfo(object):
        def __init__(self, board):
            self.name = board.name
            lst = sort_and_group(board.tasks, key=lambda x: x.project.name)
            self.project_info_list = [ProjectInfo(name, list(tasks)) for name, tasks in lst]

    return BoardInfo(board)


@app.route("/")
def index():
    board_list = [Board(name, filters) for name, filters in settings.BOARDS]
    board_info_list = [create_board_info(x) for x in board_list]

    return render_template("index.html", board_info_list=board_info_list)


@app.route("/favicon.ico")
def favicon():
    return redirect("/static/favicon.ico", 301)
