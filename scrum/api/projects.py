from flask import Blueprint

from ..services import projects

from . import route


bp = Blueprint('projects', __name__, url_prefix='/projects')

@route(bp, '/')
def all():
    """Returns the user instance of the currently authenticated user."""
    

    return projects.all()