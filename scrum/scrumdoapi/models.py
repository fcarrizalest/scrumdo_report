from ..core import db
from ..helpers import JsonSerializer

class OrganizationJsonSerializer(JsonSerializer):
    __json_public__ = ['slug', 'name']


class Organization(OrganizationJsonSerializer, db.Model):
	__tablename__ = 'organizations'

	id = db.Column(db.Integer(), primary_key=True)
	slug = db.Column(db.String(255), unique=True)
	name = db.Column(db.String(255) )
	projects = db.relationship('Project', backref="organizations" , lazy="dynamic")


class ProjectJsonSerializer(JsonSerializer):
	__json_public__ = ['slug','name','id']


class Project(ProjectJsonSerializer,db.Model):
	__tablename__ = 'projects'
	id = db.Column(db.Integer(), primary_key=True)
	slug = db.Column(db.String(255), unique=True)
	name = db.Column(db.String(255) )
	organization_id = db.Column(db.Integer,  db.ForeignKey('organizations.id'))
	organization = db.relationship('Organization', backref=db.backref('organizations', lazy='dynamic'))
	iterations = db.relationship('Iteration', backref="projects" , lazy="dynamic")

class IterationJsonSerializer(JsonSerializer):
	__json_public__ = ['id','name','story_count','start_date','end_date']

class Iteration(IterationJsonSerializer,db.Model):
	__tablename__ = 'iterations'

	id = db.Column(db.Integer(), primary_key=True)
	include_in_velocity = db.Column(db.BOOLEAN)
	locked = db.Column(db.BOOLEAN)
	name = db.Column(db.String(255) )
	default_iteration = db.Column(db.BOOLEAN)
	detail = db.Column(db.TEXT )
	start_date = db.Column( db.Date )
	iteration_type = db.Column(db.String(255) )
	story_count = db.Column(db.Integer() )
	end_date = db.Column( db.Date )
	hidden = db.Column(db.BOOLEAN)
	project_id = db.Column(db.Integer,  db.ForeignKey('projects.id'))
	project = db.relationship('Project', backref=db.backref('projects', lazy='dynamic'))

	stories = db.relationship('Story', backref='iterations',
                                lazy='dynamic')

	storiesBug = db.relationship('Story',
                                lazy='dynamic', primaryjoin="and_(Iteration.id == Story.iteration_id ,Story.all_labels =='Bug'  )")
	

story_user = db.Table(
	'story_user',
	db.Column('story_id', db.Integer(), db.ForeignKey('stories.id')),
	db.Column('user_id', db.Integer(), db.ForeignKey('users.id')))


label_story = db.Table(
	'label_story',
	db.Column('story_id', db.Integer(), db.ForeignKey('stories.id')),
	db.Column('label_id', db.Integer(), db.ForeignKey('labels.id')))


class CellJsonSerializer(JsonSerializer):
	__json_public__ =['id','full_label','label']


class Cell(CellJsonSerializer,db.Model):
	__tablename__ = 'cells'

	id = db.Column(db.Integer(), primary_key=True)
	color = db.Column(db.String(255) )
	full_label = db.Column(db.String(255) )
	label = db.Column(db.String(255) )



class LabelJsonSerializer(JsonSerializer):
	__json_public__ =['id','name','color']


class Label(LabelJsonSerializer,db.Model):
	__tablename__ = 'labels'

	id = db.Column(db.Integer(), primary_key=True)
	color = db.Column(db.String(255) )
	name = db.Column(db.String(255) )


class StoryJsonSerializer(JsonSerializer):
	__json_public__ = ['id','summary','points','users','labels','cell','iteration_id','number']

class Story(StoryJsonSerializer, db.Model):
	__tablename__ = 'stories'

	id = db.Column(db.Integer(), primary_key=True)
	completed_task_count = db.Column(db.Integer())
	age_hours = db.Column(db.Integer())
	number = db.Column(db.Integer())
	detail = db.Column(db.TEXT )
	summary = db.Column(db.TEXT )
	points = db.Column(db.Float( ) )
	users = db.relationship('User', secondary=story_user, backref=db.backref('stories', lazy='dynamic') )

	iteration_id = db.Column(db.Integer,  db.ForeignKey('iterations.id'))
	iteration = db.relationship('Iteration', backref=db.backref('iterations', lazy='dynamic'))

	cell_id = db.Column(db.Integer,  db.ForeignKey('cells.id'))
	cell = db.relationship('Cell', backref=db.backref('cells', lazy='dynamic'))

	labels = db.relationship('Label', secondary=label_story, backref=db.backref('stories', lazy='dynamic') )
	all_labels = db.Column(db.TEXT )



class UserJsonSerializer(JsonSerializer):
	__json_public__ = ['id','username','first_name','last_name']


class User(UserJsonSerializer, db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer(), primary_key=True)
	username   = db.Column(db.String(255) )
	first_name  = db.Column(db.String(255) )
	last_name = db.Column(db.String(255) )




