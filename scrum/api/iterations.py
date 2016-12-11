from flask import Blueprint

from ..services import projects,iterations,stories

from . import route


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


@route(bp, '/<str_date>')
def end_date(str_date):
    
    
    
    return iterations.find( end_date= str_date ).all()


