import webapp2
import base_handler
from db import models
from google.appengine.ext import ndb
import json


class GlobalSearchHandler(base_handler.BaseHandler):
    def get(self):
        q = self.request.get('q')
        result = models.ContentItem.search_word(q)
        self.response.content_type = "application/json"
        return self.response.write(json.dumps(result))
