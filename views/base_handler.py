"""Base handler for easy connect."""

import webapp2
import json
import logging
from webapp2_extras import jinja2
from datetime import datetime,timedelta
import urllib
from google.appengine.api import users
# jinja_environment = jinja2.Environment(autoescape=True,
#     loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), '..', 'templates')))

# jinja_environment.globals.update(gettext=gettext.gettext, ngettext=gettext.ngettext)

class BaseHandler(webapp2.RequestHandler):
  def dispatch(self):
	webapp2.RequestHandler.dispatch(self)

  @webapp2.cached_property
  def jinja2(self):
      # Returns a Jinja2 renderer cached in the app registry.
      return jinja2.get_jinja2(app=self.app,factory=jinja2_factory)

  def render_response(self, _template, **context):
      user = users.get_current_user()
      udict = {'name':'','logout_link':''}
      if user:
        udict['username'] = user.nickname()
        udict['logout_link'] = users.create_logout_url('/logout')

      context.update(udict)
      # Renders a template and writes the result to the response.
      rv = self.jinja2.render_template(_template, **context)
      self.response.write(rv)

def jinja2_factory(app):
    j = jinja2.Jinja2(app)
    j.environment.filters.update({
        'datetimeist': format_datetime,
        'get_url_for_page':get_url_for_page,
        'format_duration':format_duration
        })
    return j


class AbstractViewhandler(BaseHandler):
  def __init__(self, request, response):
   	super(AbstractViewhandler, self).__init__(request, response)
   	self.initialize(request, response)
   	self.get_methods = None # Shuld be overrden in subclass
   	self.post_methods = None # Shuld be overrden in subclass

  def get(self):
   	self._RespondToRequest(self.get_methods)

  def post(self):
    self._RespondToRequest(self.post_methods)

  def _RespondToRequest(self, methods):
	try:
		method = self.request.get('method')
		params = self.request.get('params', {})
		func = getattr(methods, method)
		kwargs = json.loads(params)
		result = func(**kwargs)
		self.response.content_type = 'application/json'
		self.response.out.write(json.dumps(result))
	except Exception as e:
		logging.info(e)
		raise


def format_datetime(value):
    if value:
        istdate = value + timedelta(hours=5,minutes=30)
        return istdate.strftime("%d-%b-%Y %I:%M %p")
    else:
        return ""

def get_url_for_page(value,path,qs):
    qs['page'] = value
    return path+'?' + urllib.urlencode(qs)

def format_duration(value):
  m, s = divmod(int(value), 60)
  fmt_duration = str(m).zfill(2)+":"+str(s).zfill(2)
  return fmt_duration

# jinja_environment.filters['datetimeist'] = format_datetime
# jinja_environment.filters['get_url_for_page'] = get_url_for_page
