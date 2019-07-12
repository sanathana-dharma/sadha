import gettext
import os
import webapp2
from datetime import datetime,timedelta
import jinja2
import urllib


def getTemplate(tempalte_name):
	"""Gets template"""
	return jinja_environment.get_template(tempalte_name)

def format_datetime(value):
    if value:
        istdate = value + timedelta(hours=5,minutes=30)
        return istdate.strftime("%d-%b-%Y %I:%M %p")
    else:
        return ""

def get_url_for_page(value,path,qs):
    qs['page'] = value
    return path+'?' + urllib.urlencode(qs)

# jinja_environment.filters['datetimeist'] = format_datetime
# jinja_environment.filters['get_url_for_page'] = get_url_for_page