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

# HANDLER FOR CONTENT ITEMS


#API for fetching category details
class API_ContentList(base_handler.BaseHandler):
  def get(self):
			#Fetch content items for selected category via ajax call

			category_id = self.request.get('category_id')
			if category_id == '' or category_id == ' ':
				category_id = None
			logging.info('category_id= %s',category_id)

			if category_id:
				logging.info('Fetch content items..')
				#Fetch content items
				content_items = models.ContentItem.get_content_items(category_id)

			dict_content_items = {}
			if content_items:
				#Lets package the data and send it out
				dict_content_items = {ci.key.id(): ci.content for ci in content_items}
				self.response.content_type = 'application/json'
				if len(dict_content_items)>0:
					self.response.out.write(json.dumps( {'dict_content_items': dict_content_items}))
				else:
					self.response.out.write(json.dumps( {'dict_content_items': dict_content_items}))




# API FOR CONTENT ITEMS
class ContentListHandler(base_handler.BaseHandler):
  def get(self):

	  		'''
			#For Dynamic categories - fetch root or child categories
			#get content items based on category provided
			category_id = self.request.get('category_id')
			if category_id == '' or category_id == ' ':
				category_id = None

			if category_id:
				#Fetch child categories
				categories = models.Category.get_child_categories(parent_category_id)
				#Fetch content items for given category
				content_items = models.ContentItem.get_content_items(category_id)
			else:
				#Fetch root categories
				categories = models.Category.get_root_categories()
			'''

			#get content items based on category provided
			category_id = self.request.get('category_id')
			if category_id == '' or category_id == ' ':
				category_id = None

			#Fetch content items
			content_items = models.ContentItem.get_content_items(category_id)

			dict_content_items = {}
			if content_items:
				#Send content items
				for c in content_items:
					dict_content_items[c.key.id()] = c

			context = {'dict_content_items': dict_content_items}
			self.render_response('content-list.html',**context)


  def post(self):
			#get child categories or fetch ROOT categories if no parameter was passed
			parent_category_id = self.request.get('parent_category_id')
			if parent_category_id:
				#Fetch child categories
				categories = models.Category.get_child_categories(parent_category_id)
			else:
				#Fetch all categories
				categories = models.Category.get_root_categories()

			dict_categories = {}
			if categories:
				#Lets package the data and send it out
				dict_categories = {cat.key.id(): cat.name for cat in categories}
				self.response.content_type = 'application/json'
				self.response.out.write(json.dumps( {'dict_categories': dict_categories}))




class AddContentHandler(base_handler.BaseHandler):
		def get(self):
			context = {}
			self.render_response('content-add.html',**context)

		def post(self):
			msg = ''
			category_id = self.request.get('dyanmic_categories_lastchild_category_id')
			content = self.request.get('content')
			logging.info('category_id=' + category_id)
			logging.info('content=' + content)

			try:
				content_item = models.ContentItem.add_content_item(content,category_id)
				if content_item:
					logging.info('Content item added succesfully.')
				else:
					logging.info('Unable to add Content.')
			except Exception as e:
				msg = 'Problem in adding content item to database. %s' % str(e)
			return self.response.out.write(json.dumps({'msg': msg}))

class EditContentHandler(base_handler.BaseHandler):
		def get(self):
			content_item_id = self.request.get('content_item_id')
			msg = ''

			content_item = models.ContentItem.get_content_item(content_item_id)

			context = {}
			if content_item:
				logging.info('Found content record!')
				category = models.Category.get_category(content_item.category_id)

				context = {'content': content_item.content, 'category_name': category.name , 'content_item_id' : content_item.key.id()}
			else:
				logging.error('Invalid content id provided!')

			self.render_response('content-edit.html',**context)

		def post(self):
			msg = ''
			content_item_id = self.request.get('content_item_id')
			new_content = self.request.get('content_item_content')

			msg = ''
			logging.info('content_item_id=' + content_item_id)
			logging.info('new_content=' + new_content)

			try:
				content_item = models.ContentItem.edit_content_item(content_item_id, new_content)
				if content_item:
					logging.info('Content item updated succesfully.')
				else:
					logging.info('Unable to update Content.')
			except Exception as e:
				msg = 'Problem in updating content item to database. %s' % str(e)
			return self.response.out.write(json.dumps({'msg': msg}))
