from flask_wtf import Form
from wtforms import SelectField


class Searh_Form(Form):

	slug = SelectField( u'slug')