from .scrumdoapi import UsersService,CellsService,LabelsService,StoriesService,OrganizationsService,ProjectsService,IterationsService


organizations = OrganizationsService()
projects = ProjectsService()
iterations = IterationsService()
users = UsersService()
stories = StoriesService()
labels = LabelsService()
cells = CellsService()