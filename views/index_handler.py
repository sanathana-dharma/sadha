import webapp2
import base_handler
from db import models
from google.appengine.ext import ndb
import jinja2_env
from views.lib.paginator import GaePaginator
import logging
import json
from google.appengine.datastore.datastore_query import Cursor
from libs import ndbpager
from google.appengine.api import users
import os


# ROOT HANDLER FOR SITE
class RedirectMainHandler(base_handler.BaseHandler):
  def get(self):
    return self.redirect("/main/index")

# API FOR CATEGORIES
class IndexHandler(base_handler.BaseHandler):
  def get(self):
		context = {}
		self.render_response('index.html',**context)
