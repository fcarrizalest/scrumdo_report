from flask import Blueprint

from ..services import projects,iterations,stories

from . import route


bp = Blueprint('projects', __name__, url_prefix='/projects')

@route(bp, '/')
def all():
    """Returns the user instance of the currently authenticated user."""
    

    return projects.all()


@route(bp,'/<id>')
def project(id):

	return projects.get_or_404(id)


@route(bp,'/<id>/iterations')
def project_iterations(id):


	return iterations.find( project_id=id ).all()


@route(bp,'/<id>/iterations/<interation_id>')
def iterations_stories(id,interation_id):


	return stories.find( iteration_id= interation_id ).all()