#!/usr/bin/python
#
# Copyright 2011 Google Inc. All Rights Reserved.

"""A simple guest book app that demonstrates the App Engine search API."""

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


from cgi import parse_qs
from datetime import datetime
import os
import string
import urllib
from urlparse import urlparse
from webapp2_extras import jinja2

from google.appengine.api import search
from google.appengine.api import users

_INDEX_NAME = 'greeting'

# _ENCODE_TRANS_TABLE = string.maketrans('-: .@', '_____')

class MainSearchPage(base_handler.BaseHandler):
    """Handles search requests for comments."""

    def get(self):
        """Handles a get request with a query."""
        uri = urlparse(self.request.uri)
        query = ''
        if uri.query:
            query = parse_qs(uri.query)
            query = query['query'][0]

        # sort results by author descending
        expr_list = [search.SortExpression(
            expression='author', default_value='',
            direction=search.SortExpression.DESCENDING)]
        # construct the sort options
        sort_opts = search.SortOptions(
             expressions=expr_list)
        query_options = search.QueryOptions(
            limit=77,
            sort_options=sort_opts)
        query_obj = search.Query(query_string=query, options=query_options)
        results = search.Index(name=_INDEX_NAME).search(query=query_obj)
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'results': results,
            'number_returned': len(results.results),
            'url': url,
            'url_linktext': url_linktext,
        }

        context = {'template_values': template_values}
        #self.render_response('search.html',template_values)
        self.render_template('search.html', template_values)


def CreateDocument(author, content):
    """Creates a search.Document from content written by the author."""
    if author:
        nickname = author.nickname().split('@')[0]
    else:
        nickname = 'anonymous'
    # Let the search service supply the document id.
    return search.Document(
        fields=[search.TextField(name='author', value=nickname),
                search.TextField(name='comment', value=content),
                search.DateField(name='date', value=datetime.now().date())])


class SearchComment(base_handler.BaseHandler):
    """Handles requests to index comments."""

    def post(self):
        """Handles a post request."""
        author = None
        if users.get_current_user():
            author = users.get_current_user()

        content = self.request.get('content')
        query = self.request.get('search')
        if content:
            search.Index(name=_INDEX_NAME).put(CreateDocument(author, content))
        if query:
            self.redirect('/main/search?' + urllib.urlencode(
                #{'query': query}))
                {'query': query.encode('utf-8')}))
        else:
            self.redirect('/main/search')
