from flask import Blueprint

from ..services import projects,iterations,stories

from . import route


bp = Blueprint('stories', __name__, url_prefix='/stories')

@route(bp, '/')
def all():
    

    return stories.all()


@route(bp,'/<id>')
def story(id):

	return stories.get_or_404(id)

