# Python 2/3 compatibility
from __future__ import division, absolute_import, print_function, unicode_literals

from datetime import datetime, timedelta

from sqlobject import AND, LIKE
from sqlobject.sqlbuilder import LEFTJOINOn, IN

from yokadi.core.db import Task, TaskKeyword, Project
from yokadi.ycli import parseutils

NOTE_KEYWORD = "_note"


def compute_min_date():
    now = datetime.now()
    return now - timedelta(now.weekday())


def list_tasks(status, project_list, filters):
    lst = Task.select(
            AND(IN(Task.q.project, project_list),
                Task.q.status == status,
                *filters),
            orderBy=Task.q.id, distinct=True,
            join=LEFTJOINOn(Task, TaskKeyword, Task.q.id == TaskKeyword.q.taskID)
        )
    return list(lst)


class Board(object):
    def __init__(self, name, filter_string):
        self.name = name

        project_name, keyword_filters = parseutils.extractKeywords(filter_string)
        project_list = Project.select(LIKE(Project.q.name, project_name))

        q_filters = [x.filter() for x in keyword_filters]

        # Skip notes
        q_filters.append(parseutils.KeywordFilter("!@" + NOTE_KEYWORD).filter())

        self.tasks = {}

        self.tasks["new"] = list_tasks('new', project_list, q_filters)
        self.tasks["started"] = list_tasks('started', project_list, q_filters)
        min_date = compute_min_date()
        self.tasks["done"] = list_tasks('done', project_list, q_filters + [Task.q.doneDate >= min_date])
