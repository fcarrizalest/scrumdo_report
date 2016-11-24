from flask import session,flash,url_for,redirect,request,Blueprint, render_template
from ..core import db
from . import route
from scrum.settings import scrumdo_username, scrumdo_password, scrumdo_host
import slumber

from .forms import Searh_Form
from ..services import iterations

import datetime


bp = Blueprint('dashboard', __name__)

@route(bp, '/',methods=('GET','POST'))
def index():
	form = Searh_Form()


	today = datetime.date.today()

	end_date = today + datetime.timedelta( (2-today.weekday()) % 7 )

	str_date = end_date.strftime('%Y-%m-%d')

	# str_date = '2016-11-23'


	iteration_list = iterations.find( end_date= str_date )






	return render_template('index.html', end_date= str_date, iteration_list=iteration_list)


# Since we're iterating over your entire account in this example, there could be a lot of API calls.
# This function is a dumb way to make sure we don't go over the throttle limit.
def check_throttle(requests):	
	requests += 1
	if requests >= 149: 
		sleep(5) # Add in a delay when we get close the our max # of requests per 5 seconds.
		return 0
	return requests
