from functools import wraps

from flask import jsonify


from ..core import ScrumError, ScrumFormError
from ..helpers import JSONEncoder
from .. import factory

from ..core import Service
from .models import Organization,Project,Iteration,User,Story,Label,Cell


class OrganizationsService(Service):
    __model__ = Organization


class ProjectsService(Service):
    __model__ = Project


class IterationsService(Service):
    __model__ = Iteration

class UsersService(Service):
    __model__ = User

class StoriesService(Service):
    __model__ = Story

class LabelsService(Service):
    __model__ = Label

class CellsService(Service):
    __model__ = Cell


def create_app(settings_override=None, register_security_blueprint=False):
    """Returns the Overholt API application instance"""

    app = factory.create_app(__name__, __path__, settings_override,
                             register_security_blueprint=register_security_blueprint)

    # Set the default JSON encoder
    app.json_encoder = JSONEncoder

    # Register custom error handlers
    app.errorhandler(ScrumError)(on_scrum_error)
    app.errorhandler(ScrumFormError)(on_scrum_form_error)
    app.errorhandler(404)(on_404)

    return app

def route(bp, *args, **kwargs):
    kwargs.setdefault('strict_slashes', False)

    def decorator(f):
        @bp.route(*args, **kwargs)
        @wraps(f)
        def wrapper(*args, **kwargs):
            sc = 200
            rv = f(*args, **kwargs)
            if isinstance(rv, tuple):
                sc = rv[1]
                rv = rv[0]
            return jsonify(dict(data=rv)), sc
        return f

    return decorator



def on_scrum_error(e):

    print "encontre un error "
    return jsonify(dict(error=e.msg)), 400


def on_scrum_form_error(e):
    return jsonify(dict(errors=e.errors)), 400


def on_404(e):
    return jsonify(dict(error='Not found')), 404