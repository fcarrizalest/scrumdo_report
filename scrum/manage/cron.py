from flask import current_app
from flask_script import Command, prompt, prompt_pass
from werkzeug.datastructures import MultiDict
from time import sleep

from ..core import db
from scrum.settings import scrumdo_username, scrumdo_password, scrumdo_host
import slumber

from ..services import organizations,projects,iterations,users,stories
from datetime import datetime

class LogCommand(Command):

	def run(self):
		print "Iniciando"
		base_url = "%s/api/v3/" % scrumdo_host
		api = slumber.API(base_url, auth=(scrumdo_username, scrumdo_password))

		iteration_list = iterations.all()
		api_count = self.check_throttle(1)
		for iteration in iteration_list:
			print "1"

			story_list = api.organizations(iteration.project.organization.slug).projects(iteration.project.slug).iterations(iteration.id).stories.get()
			api_count = self.check_throttle(api_count)

			for story in story_list:
				print "2"

				print story

				db_users = []


				for user_api in story['assignee']:

					db_user = users.first(id = user_api['id'] )

					if not db_user:
						print "Creando usuario"
						print user_api['first_name']

						new_user = users.new( 
							id = user_api['id'], 
							username = user_api['username'], 
							first_name = user_api['first_name'],  
							last_name = user_api['last_name'] )

						db_user = users.save( new_user )

					db_users.append( db_user  )

				db_story = stories.first( id = story['id'] )

				if( not db_story ):

					print "Creando story"
					print story['summary']

					new_story = stories.new(
						id= story['id'],
						completed_task_count = story['completed_task_count'],
						age_hours = story['age_hours'],
						number = story['number'],
						detail = story['detail'],
						summary = story['summary'],
						points = story['points'],
						users = db_users ,
						iteration_id = story['iteration_id']

						)

					db_story = stories.save(new_story)


				db_story.completed_task_count = story['completed_task_count']
				db_story.age_hours = story['age_hours']
				db_story.number = story['number']
				db_story.detail = story['detail']
				db_story.summary = story['summary']

				if(story['points'] == '?'):
					story['points'] = 0

				db_story.points = story['points']
				db_story.users = db_users
				db_story.iteration_id = story['iteration_id']

				db_story = stories.save(db_story)












					


	def check_throttle(self, requests):
		requests += 1
		if requests >= 149: 
			sleep(5) # Add in a delay when we get close the our max # of requests per 5 seconds.
			return 0
		return requests


class CronCommand(Command):

	def run(self):

		base_url = "%s/api/v3/" % scrumdo_host
		api = slumber.API(base_url, auth=(scrumdo_username, scrumdo_password))

		organization_list = api.organizations.get()
		api_count = self.check_throttle(1)

		for org in organization_list:

			db_org = organizations.first( id=org['id'] )

			if(not db_org):
				print "Creando Organizacion"
				print org['name']

				new_org = organizations.new( id=org['id'], name=org['name'],  slug=org['slug'] )
				db_org = organizations.save(new_org)

			slug = db_org.slug
			project_list = api.organizations( slug ).projects.get()
			api_count = self.check_throttle(api_count)

			for project in project_list:

				db_project = projects.first( id=project['id'] )

				if( not db_project ):
					print "Creando proyecto"
					print project['name']
					new_project = projects.new( id=project['id'], name = project['name'] , slug=project['slug'], organization_id = db_org.id )
					db_project = projects.save(new_project)

				iteration_list = api.organizations(db_org.slug).projects(db_project.slug).iterations.get()
				api_count = self.check_throttle(api_count)

				for iteration in iteration_list:

					print iteration

					db_iteration = iterations.first( id = iteration['id'] )

					if(not db_iteration ):
						print "creando interacion"

						if( iteration['start_date'] == None ):
							iteration['start_date'] = '2000-01-01'

						if( iteration['end_date'] == None ):
							iteration['end_date'] = '2000-01-01'




						start_date = datetime.strptime(iteration['start_date'], '%Y-%m-%d')
						end_date = datetime.strptime(iteration['end_date'], '%Y-%m-%d')
						

						new_iteration = iterations.new(  
							id = iteration['id'],
							include_in_velocity = iteration['include_in_velocity'],
							locked = iteration['locked'],
							name = iteration['name'],
							default_iteration = iteration['default_iteration'],
							detail = iteration['detail'],
							start_date = start_date,
							iteration_type = iteration['iteration_type'],
							story_count = iteration['story_count'],
							end_date = end_date,
							hidden = iteration['hidden'],
							project_id = db_project.id


						  )
						db_iteration = iterations.save(new_iteration)

					if( iteration['start_date'] == None ):
						iteration['start_date'] = '2000-01-01'

					if( iteration['end_date'] == None ):
						iteration['end_date'] = '2000-01-01'

					db_iteration.id = iteration['id']
					db_iteration.include_in_velocity = iteration['include_in_velocity']
					db_iteration.locked = iteration['locked']
					db_iteration.name = iteration['name']
					db_iteration.default_iteration = iteration['default_iteration']
					db_iteration.detail = iteration['detail']

					start_date = datetime.strptime(iteration['start_date'], '%Y-%m-%d')
					db_iteration.start_date = start_date


					db_iteration.iteration_type = iteration['iteration_type']
					db_iteration.story_count = iteration['story_count']

					end_date = datetime.strptime(iteration['end_date'], '%Y-%m-%d')

					db_iteration.end_date = end_date
					db_iteration.hidden = iteration['hidden']
					db_iteration.project_id = db_project.id

					db_iteration = iterations.save(db_iteration);



	def check_throttle(self, requests):
		requests += 1
		if requests >= 149: 
			sleep(5) # Add in a delay when we get close the our max # of requests per 5 seconds.
			return 0
		return requests

