# Python 2/3 compatibility
from __future__ import division, absolute_import, print_function, unicode_literals

from datetime import datetime, timedelta

from sqlobject import AND, OR, LIKE
from sqlobject.sqlbuilder import LEFTJOINOn, IN

from yokadi.core.db import Task, TaskKeyword, Project
from yokadi.ycli import parseutils

NOTE_KEYWORD = "_note"


def compute_min_date():
    now = datetime.now()
    return now - timedelta(now.weekday())


class Board(object):
    __slots__ = ("name", "tasks")
    def __init__(self, name, filter_string):
        self.name = name

        project_name, keyword_filters = parseutils.extractKeywords(filter_string)

        q_filters = [x.filter() for x in keyword_filters]

        project_list = Project.select(LIKE(Project.q.name, project_name))
        q_filters.append(IN(Task.q.project, project_list))

        # Skip notes
        q_filters.append(parseutils.KeywordFilter("!@" + NOTE_KEYWORD).filter())

        # Only list done tasks if they were done after min_date
        min_date = compute_min_date()
        q_filters.append(OR(
            Task.q.status != 'done',
            Task.q.doneDate >= min_date
            ))

        self.tasks = Task.select(
            AND(*q_filters),
            orderBy=Task.q.id, distinct=True,
            join=LEFTJOINOn(Task, TaskKeyword, Task.q.id == TaskKeyword.q.taskID)
        )
