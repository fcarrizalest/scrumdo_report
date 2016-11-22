from .scrumdoapi import UsersService,StoriesService,OrganizationsService,ProjectsService,IterationsService


organizations = OrganizationsService()
projects = ProjectsService()
iterations = IterationsService()
users = UsersService()
stories = StoriesService()