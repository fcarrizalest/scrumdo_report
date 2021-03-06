from flask import session,flash,url_for,redirect,request,Blueprint, render_template
from ..core import db
from . import route
from scrum.settings import scrumdo_username, scrumdo_password, scrumdo_host
import slumber
from sqlalchemy.sql import text

from .forms import Searh_Form
from ..services import iterations,users

from ..manage.cron import CronCommand,LogCommand

import datetime

from rq import Queue
import os
import redis


from flask_script import Manager

from ..scrumdoapi import create_app



redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)


bp = Blueprint('dashboard', __name__)

@route(bp, '/',methods=('GET','POST'))
def index():

	select_list_rows = db.engine.execute(text('SELECT iterations.end_date \
									 FROM iterations \
									 GROUP BY iterations.end_date order by iterations.end_date DESC LIMIT 10'))

	sql = "\
		SELECT t.name as name,	\
				t.points as points,\
				t.end_date as end_date\
			FROM (\
				SELECT 	SUM(stories.points) as points,\
			  			min(projects.name) as name,\
			  			min(projects.id) as id,\
			  			min(iterations.end_date) as end_date\
			  	FROM stories\
			   	INNER JOIN\
					iterations ON iterations.id = stories.iteration_id\
				INNER JOIN	\
					projects ON projects.id = iterations.project_id\
				WHERE iterations.end_date IN ( SELECT iterations.end_date \
									 FROM iterations \
									 GROUP BY iterations.end_date order by iterations.end_date DESC LIMIT 10 )\
				GROUP BY projects.id,\
				iterations.end_date\
				ORDER BY points\
				) as t\
		ORDER BY name\
	"

	select_list = []
	
	for row in select_list_rows:
		select_list.append(row)
	
	
	projects_list = []
	urows = db.engine.execute(text(sql))
	for row in urows:
		projects_list.append(row)

	return render_template('index.html',select_list=select_list, projects_list=projects_list )

@route(bp, '/r1',methods=('GET','POST'))
def r1():
	form = Searh_Form()


	today = datetime.date.today()

	end_date = today + datetime.timedelta( (2-today.weekday()) % 7 )

	str_date = end_date.strftime('%Y-%m-%d')

	# str_date = '2016-08-10'


	


	select_list = db.engine.execute(text('SELECT iterations.end_date \
									 FROM iterations \
									 GROUP BY iterations.end_date order by iterations.end_date DESC'))

	choices = [( str(x.end_date), x.end_date) for x in select_list]

	form.end_date.choices = choices

	if form.validate_on_submit():
		str_date = request.values.get('end_date')
	else:
		form.end_date.default = str_date
		form.process()

	


	iteration_list = iterations.find( end_date= str_date )

	


	sql = " SELECT projects.name as pname, \
				  iterations.name, \
				  iterations.end_date, \
				  coalesce( NULLIF(iterations.story_count,0),0) as story_count, \
				  ( \
				  	  SELECT coalesce( NULLIF( SUM( stories.points ),0 ) ,0) as spoints\
				  	  FROM stories \
				  	  WHERE stories.iteration_id = iterations.id \
				   ) as spoints, \
				   	( \
				  	  SELECT coalesce( NULLIF( SUM( stories.points ) ,0) , 0) as sbpoints \
				  	  FROM stories \
				  	  WHERE stories.iteration_id = iterations.id AND\
				  	  		stories.all_labels = 'Bug' \
				   ) as sbpoints, \
					( \
				  	  SELECT coalesce( NULLIF( COUNT( stories.id ),0) , 0) as sb \
				  	  FROM stories \
				  	  WHERE stories.iteration_id = iterations.id AND\
				  	  		stories.all_labels = 'Bug' \
				   ) as sb, \
					( \
				  	  SELECT coalesce( NULLIF( SUM( stories.points ),0) , 0) as sb \
				  	  FROM stories \
				  	  WHERE stories.iteration_id = iterations.id AND\
				  	  		stories.cell_id in (\
				  	  			SELECT id \
				  	  			FROM cells\
				  	  			WHERE cells.label != 'Todo' AND\
				  	  				  cells.label != 'Doing'\
				  	  		 ) \
				   ) as terminados, \
				   coalesce( NULLIF( (  \
				   	 SELECT  coalesce( NULLIF( COUNT(  stories.id ),0) , 0)  as trabajando \
				  	  FROM stories \
				  	  WHERE stories.iteration_id = iterations.id AND\
				  	  		stories.cell_id in (\
				  	  			SELECT id \
				  	  			FROM cells\
				  	  			WHERE \
				  	  				  cells.label = 'Doing'\
				  	  		 ) GROUP BY stories.iteration_id \
				   	),0) , 0) as trabajando,	\
					coalesce( NULLIF( (  \
				   	 SELECT  coalesce( NULLIF( SUM(  stories.points ),0) , 0)  as trabajando \
				  	  FROM stories \
				  	  WHERE stories.iteration_id = iterations.id AND\
				  	  		stories.cell_id in (\
				  	  			SELECT id \
				  	  			FROM cells\
				  	  			WHERE \
				  	  				  cells.label = 'Doing'\
				  	  		 ) GROUP BY stories.iteration_id \
				   	),0) , 0) as trabajandopuntos	\
			FROM iterations \
			INNER JOIN projects ON iterations.project_id = projects.id \
			WHERE  iterations.end_date = :end_date \
			"

	d = db.engine.execute(text(sql),  bug ="Bug" , end_date=str_date)

	rows = []

	for row in d:
		row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in row.__table__.columns}
		print row2dict
		print row
		rows.append(row)

	sql = "SELECT 	users.username,\
					users.first_name,\
					COUNT(stories.id) as total,\
					SUM(stories.points)  as puntos,\
					coalesce( NULLIF(   MAX(t.puntos)  ,0),0) as p_trabajando,\
					 coalesce( NULLIF( MAX(t.projects), ' ') ,' ') as projects \
			FROM story_user\
			INNER JOIN\
				stories ON stories.id = story_user.story_id\
			INNER JOIN \
				users ON users.id = story_user.user_id\
			INNER JOIN\
				iterations ON iterations.id = stories.iteration_id AND\
				iterations.end_date = :end_date\
			INNER JOIN projects ON iterations.project_id = projects.id\
			LEFT JOIN (\
					SELECT 	users.id,users.username,\
					users.first_name,\
					COUNT(stories.id) as total,\
					coalesce( NULLIF(  SUM(stories.points)  ,0) , 0) as puntos,\
					string_agg(projects.name,',') as projects\
					FROM story_user\
						INNER JOIN\
							stories ON stories.id = story_user.story_id\
						INNER JOIN \
							users ON users.id = story_user.user_id\
						INNER JOIN\
							iterations ON iterations.id = stories.iteration_id AND\
							iterations.end_date = :end_date2 AND\
							stories.cell_id in (\
							  	  			SELECT id \
							  	  			FROM cells\
							  	  			WHERE \
							  	  				  cells.label = 'Doing'\
							  	  		 )\
						INNER JOIN projects ON iterations.project_id = projects.id\
						GROUP BY users.id\
				) as t ON t.id = users.id \
			GROUP BY users.id\
		  "


	urows = db.engine.execute(text(sql), end_date=str_date,end_date2=str_date )

	u = []
	for row in urows:
		u.append(row)











	return render_template('r1.html',
		form = form, 
		select_list=select_list, 
		rows=rows,
		users=u, 
		end_date= str_date, 
		iteration_list=iteration_list)


@route(bp, '/r3',methods=('GET','POST') )
def r3():

	sql = "SELECT t.name as name  , SUM(t.bugs) as bp , SUM(t.puntos) as points \
FROM \
( \
( \
SELECT\
    projects.name,\
    SUM(stories.points) as bugs,\
    0 as puntos \
FROM stories \
INNER JOIN iterations on iterations.id = stories.iteration_id \
INNER JOIN projects on projects.id = iterations.project_id \
WHERE stories.id IN ( select story_id  from label_story WHERE label_id IN ( select id from labels where name like '%Bug%' )  ) \
GROUP BY projects.name \
ORDER BY SUM(stories.points) \
) \
UNION ( \
SELECT\
    projects.name,\
    0 as bugs,\
    SUM(stories.points) as puntos \
FROM stories \
INNER JOIN iterations on iterations.id = stories.iteration_id \
INNER JOIN projects on projects.id = iterations.project_id \
GROUP BY projects.name \
ORDER BY SUM(stories.points) \
) ) as t  GROUP BY t.name ORDER BY bp \
	"


	
	av = []
	urows = db.engine.execute(text(sql))
	for row in urows:
		av.append(row)


	return render_template('r3.html',av=av)





@route(bp, '/r2',methods=('GET','POST'))
def r2():
	sql = "SELECT 	users.username,\
					min(users.first_name) as first_name,\
					min( iterations.end_date ) as end_date,\
					min( iterations.start_date) as start_date,\
					COUNT(stories.id) as total,\
					SUM(stories.points) as puntos\
			FROM story_user\
			INNER JOIN\
				stories ON stories.id = story_user.story_id\
			INNER JOIN \
				users ON users.id = story_user.user_id\
			INNER JOIN\
				iterations ON iterations.id = stories.iteration_id\
			WHERE iterations.end_date > '2016-10-01' 	\
			GROUP BY iterations.end_date , users.username\
			ORDER BY  users.username DESC,iterations.end_date DESC\
		  "


	urows = db.engine.execute(text(sql))

	u = []
	for row in urows:
		u.append(row)

	sql = " SELECT t.username, AVG(puntos) as puntos  FROM ( " + sql + " ) as t GROUP BY username ORDER BY t.username  "

	av = []
	urows = db.engine.execute(text(sql))
	for row in urows:
		av.append(row)

	 	
	return render_template('r2.html',u=u,av=av)

@route(bp, '/r4',methods=('GET','POST'))
def r4():
	sql = " SELECT   iterations.end_date , SUM( stories.points ) as puntos \
			FROM  stories \
			INNER JOIN iterations ON iterations.id = stories.iteration_id\
			WHERE iterations.end_date > '2016-10-01'\
			GROUP BY iterations.end_date\
			ORDER BY iterations.end_date DESC"

	rows = []
	urows = db.engine.execute(text(sql))
	for row in urows:
		rows.append(row)

	return render_template('r4.html', rows=rows )


@route(bp, '/r5',methods=('GET','POST'))
def r5():
	sql = " SELECT   iterations.end_date,projects.name as project, iterations.name,   \
				( \
				  	  SELECT coalesce( NULLIF( SUM( stories.points ),0) , 0) as sb \
				  	  FROM stories \
				  	  WHERE stories.iteration_id = iterations.id AND\
				  	  		stories.cell_id in (\
				  	  			SELECT id \
				  	  			FROM cells\
				  	  			WHERE cells.label != 'Todo' AND\
				  	  				  cells.label != 'Doing'\
				  	  		 ) \
				   ) as terminados\
			FROM  iterations \
			INNER JOIN projects ON iterations.project_id = projects.id \
			WHERE iterations.end_date > '2016-10-01'\
			ORDER BY projects.name,iterations.end_date  DESC"

	rows = []
	urows = db.engine.execute(text(sql))
	for row in urows:
		rows.append(row)

	return render_template('r5.html', rows=rows )

def buscar():
	today = datetime.date.today()

	end_date = today + datetime.timedelta( (2-today.weekday()) % 7 )

	str_date = end_date.strftime('%Y-%m-%d')


	manager = Manager(create_app())
	l = LogCommand()
	l.str_date = str_date

	manager.add_command('log', l )

	manager.run(None,'log' )
	return 'ok'


def actualizatodo():
	today = datetime.date.today()

	end_date = today + datetime.timedelta( (2-today.weekday()) % 7 )

	str_date = end_date.strftime('%Y-%m-%d')


	manager = Manager(create_app())
	l = LogCommand()

	manager.add_command('log', l )

	manager.run(None,'log' )
	return 'ok'


@route(bp, '/all',methods=('GET','POST'))
def all():
	
	q = Queue(connection=conn)
	result = q.enqueue(actualizatodo,timeout=3000)
	
	return redirect(url_for('.index'))

@route(bp, '/log',methods=('GET','POST'))
def log():
	
	q = Queue(connection=conn)
	result = q.enqueue(buscar)
	
	return redirect(url_for('.index'))


def buscarcron():
	manager = Manager(create_app())
	manager.add_command('cron', CronCommand())

	manager.run(None,'cron' )

	return 'ok'
@route(bp, '/cron',methods=('GET','POST'))
def cron():
	
	q = Queue(connection=conn)
	result = q.enqueue(buscarcron)
	
	
	return redirect(url_for('.index'))



@route(bp, '/iniciadb',methods=('GET','POST'))
def iniciadb():
	db.drop_all()
	db.create_all()
	return redirect(url_for('.index'))
	
# Since we're iterating over your entire account in this example, there could be a lot of API calls.
# This function is a dumb way to make sure we don't go over the throttle limit.
def check_throttle(requests):	
	requests += 1
	if requests >= 149: 
		sleep(5) # Add in a delay when we get close the our max # of requests per 5 seconds.
		return 0
	return requests
