from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .core import db,csrf
from .helpers import register_blueprints
from .middleware import HTTPMethodOverrideMiddleware

import os

def create_app(	package_name, package_path, 
				settings_override=None,
               	register_security_blueprint=True):
	
	app = Flask(package_name, instance_relative_config=True, static_folder='../static',template_folder="../templates" )
	
	app.config.from_object('scrum.settings')
	app.config.from_object(settings_override)
	db.init_app(app)
	csrf.init_app(app)
	

	register_blueprints(app, package_name, package_path)

	app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)

	return app