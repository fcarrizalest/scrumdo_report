from flask import session,flash,url_for,redirect,request,Blueprint, render_template
from ..core import db
from . import route
from scrum.settings import scrumdo_username, scrumdo_password, scrumdo_host
import slumber
from sqlalchemy.sql import text

from .forms import Searh_Form
from ..services import iterations,users

import datetime


bp = Blueprint('dashboard', __name__)

@route(bp, '/',methods=('GET','POST'))
def index():
	form = Searh_Form()


	today = datetime.date.today()

	end_date = today + datetime.timedelta( (2-today.weekday()) % 7 )

	str_date = end_date.strftime('%Y-%m-%d')

	# str_date = '2016-08-10'


	


	select_list = db.engine.execute(text('SELECT iterations.end_date \
									 FROM iterations \
									 GROUP BY iterations.end_date'))

	choices = [( str(x.end_date), x.end_date) for x in select_list]

	form.end_date.choices = choices

	if form.validate_on_submit():
		str_date = request.values.get('end_date')
	else:
		form.end_date.default = str_date
		form.process()

	


	iteration_list = iterations.find( end_date= str_date )

	


	sql = " SELECT projects.name as PName, \
				  iterations.name, \
				  iterations.end_date, \
				  iterations.story_count, \
				  ( \
				  	  SELECT coalesce(SUM( stories.points ) ,0)\
				  	  FROM stories \
				  	  WHERE stories.iteration_id = iterations.id \
				   ) as SPoints, \
				   	( \
				  	  SELECT coalesce( SUM( stories.points ) , 0) \
				  	  FROM stories \
				  	  WHERE stories.iteration_id = iterations.id AND\
				  	  		stories.all_labels = 'Bug' \
				   ) as SBPoints, \
					( \
				  	  SELECT coalesce( COUNT( stories.id ) , 0) \
				  	  FROM stories \
				  	  WHERE stories.iteration_id = iterations.id AND\
				  	  		stories.all_labels = 'Bug' \
				   ) as SB \
			FROM iterations \
			INNER JOIN projects ON iterations.project_id = projects.id \
			WHERE  iterations.end_date = :end_date \
			"

	d = db.engine.execute(text(sql),  bug ="Bug" , end_date=str_date)

	rows = []

	for row in d:
		rows.append(row)

	sql = "SELECT 	users.username,\
					users.first_name,\
					COUNT(stories.id) as total,\
					SUM(stories.points) as puntos\
			FROM story_user\
			INNER JOIN\
				stories ON stories.id = story_user.story_id\
			INNER JOIN \
				users ON users.id = story_user.user_id\
			INNER JOIN\
				iterations ON iterations.id = stories.iteration_id AND\
				iterations.end_date = :end_date\
			GROUP BY users.id\
		  "


	urows = db.engine.execute(text(sql), end_date=str_date )

	u = []
	for row in urows:
		u.append(row)











	return render_template('index.html',
		form = form, 
		select_list=select_list, 
		rows=rows,
		users=u, 
		end_date= str_date, 
		iteration_list=iteration_list)

@route(bp, '/r2',methods=('GET','POST'))
def r2():
	sql = "SELECT 	users.username,\
					users.first_name,\
					iterations.end_date,\
					iterations.start_date,\
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


	urows = db.engine.execute(sql)

	u = []
	for row in urows:
		u.append(row)
	return render_template('r2.html',u=u)


@route(bp, '/iniciadb',methods=('GET','POST'))
def iniciadb():
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
