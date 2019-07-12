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


class TestApi(base_handler.BaseHandler):
    def get(self):
        context = {}
        return self.render_response("test-api.html",**context)



class HelloWordApi(base_handler.BaseHandler):
    def post(self):
        apikey = self.request.get('api_key','--')
        echo_string = self.request.get('echo_test')
        # account = models.Accounts.query(models.Accounts.api_key==apikey).fetch()
        resp = {}
        self.response.content_type = 'application/json'
        resp['client_ip'] = self.request.remote_addr
        if apikey == 'HELLOWORLDAPIKEY12345':
            resp['payload'] = {'data':'content goes here','echo_test':echo_string}
            resp['status'] = 'success'
            return self.response.out.write(json.dumps(resp))
        resp['status'] = 'fail'
        resp['payload'] = {'api_key':'Invalid api key'}
        return self.response.write(json.dumps(resp))
