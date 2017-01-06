from flask import Blueprint

from ..services import projects,iterations,stories
from ..core import db
from . import route

from sqlalchemy.sql import text


bp = Blueprint('iterations', __name__, url_prefix='/iterations')



@route(bp, '/')
def all():
    
    

    return iterations.all()


@route(bp, '/<int:id>')
def iteration(id):
    iterations.__model__.__json_public__.append('project')
    
    
    return iterations.get_or_404(id)


@route(bp, '/<int:id>/stories')
def iteration_stories(id):
    
    iteration = iterations.get_or_404(id)

    
    
    return iteration.stories.all()


@route(bp, '/actual')
def actual( ):
    select_list = db.engine.execute(text('SELECT iterations.end_date \
                                     FROM iterations \
                                     GROUP BY iterations.end_date order by iterations.end_date DESC limit 1'))
    str_date = ""
    for row in select_list:
        str_date = row['end_date']

    
    
    return iterations.find( end_date= str_date ).all()


@route(bp, '/<str_date>')
def end_date(str_date):
    
    
    
    return iterations.find( end_date= str_date ).all()


