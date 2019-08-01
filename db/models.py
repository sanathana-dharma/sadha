"""Models for Sadha"""

import logging
from google.appengine.ext import ndb,db
from collections import OrderedDict
import re
import random
from datetime import datetime
import itertools

class NdbError(Exception):pass

class Category(ndb.Model):
		""" Represents a container to store sentences.
			  It is possible that multiple containers can be arranged in a hierarchy to form a more complex structure
			  Eg. For Vedas
			  Veda (Content rec)
			  - Samhita (Content rec)
			  ---- Mandala (Content rec)
			  ------- Sooktha (Content rec)
		"""
		name = ndb.StringProperty(required=True)
		parent_category_id = ndb.StringProperty(default=None)
		has_child = ndb.BooleanProperty(default=False)
		created_time = ndb.DateTimeProperty(auto_now_add=True)
		updated_time = ndb.DateTimeProperty(auto_now=True)

		@classmethod
		def add_category(cls, name, parent_category_id):
			if not name:
				logging.error('Please enter  a category name!')
			if not parent_category_id:
				#no parent, so this is a root category
				logging.info('no parent exist, this is a root category')
				parent_category_id = None
			else:
				#parent exists
				logging.info('parent exists, this is a child category')

				#update parent category, set has_child to True
				logging.info('Updating parent category, set has_child = True, parent_category_id='+ parent_category_id)
				parent_category = cls.get_by_id(long(parent_category_id))
				parent_category.has_child = True
				parent_category.put()
				logging.info('Done!')

			#Save category to database
			category = cls(name=name, parent_category_id=parent_category_id)
			category = category.put()
			logging.info('Done!')
			return category

		@classmethod
		def edit_category(cls, category_id, category_name_new):
			logging.info('Editing category: '+ category_id)
			category = cls.get_by_id(long(category_id))
			category.name = category_name_new
			category = category.put()
			logging.info('Done!')
			return category

		@classmethod
		def get_root_categories(cls):
			logging.info("Returning root categories..")
			categories = cls.query(cls.parent_category_id==None).order(cls.name).fetch()
			if not categories:
				logging.info("No root categories exist.")
			return categories

		@classmethod
		def get_child_categories(cls, parent_category_id):
			if parent_category_id:
				categories = cls.query(cls.parent_category_id==str(parent_category_id)).order(cls.name).fetch()
				if categories:
					logging.info("Returning child categories..")
					return categories
				else:
					logging.info("No child categories exist for this parent.")
					return None
			else:
				logging.info("Invalid parent category, cannot fetch child categories.")
				return None

		@classmethod
		def get_all_categories(cls):
			logging.info("Returning ALL categories..")
			categories = cls.query().order(cls.name).fetch()
			if not categories:
				logging.info("No categories exist.")
			return categories

		@classmethod
		def add_root_category(cls, name):
			if not name:
				logging.error('Please enter  a category name!')
			else:
				category = cls(name=name)
			category = category.put()
			return category

		@classmethod
		def get_category(cls, category_id):
			logging.info('get_category() category_id ='+str(category_id))
			category = cls.get_by_id(long(category_id))
			return category

		@classmethod
		def get_categories_pages(cls):
			return cls.query()

		@classmethod
		def get_parent_record(cls):
			category_rec = models.Category.get_category(parent_category_id)
			if category_rec.parent_category_id:
				return models.Category.get_category(category_rec.parent_category_id)
			return None


class ContentItem(ndb.Model):
		"""Represents a Basic building block of a sooktha, sloka etc It could also be a page or entire content of a chapter.
		Levels examples:
		Ramayana (ithihasa/grantha/mahakavya)  khand ->  adhyaya ->  sarga ->  sloka
		Vedas:  samhitha ->   mandala ->  ashtaka  ->  sookta ->  mantra
		Books: Part 1 -> Chapter X

		"""
		content = ndb.StringProperty(required=True)
		category_id = ndb.StringProperty(required=True)
		sort_order = ndb.IntegerProperty()
		created_time = ndb.DateTimeProperty(auto_now_add=True)
		updated_time = ndb.DateTimeProperty(auto_now=True)

		@classmethod
		def add_content_item(cls, content, category_id):
			if not content:
				logging.error('Please enter valid content!')
			if not category_id:
				#Category not selected
				logging.error('Please select a category')
			else:
				#All good, lets create the record
				logging.info('Creating content item record..')
				content_item = cls(content=content, category_id=category_id)
				content_item = content_item.put()
				logging.info('Done!')
				return content_item

		@classmethod
		def edit_content_item(cls, content_item_id, new_content):
			logging.info('Editing content item %s, with new content=%s', content_item_id, new_content)
			content_item = cls.get_by_id(long(content_item_id))
			content_item.content = new_content
			content_item = content_item.put()
			logging.info('Done!')
			return content_item

		@classmethod
		def get_content_item(cls, content_item_id):
			logging.info('Fetching single content item, content_item_id =%s', content_item_id)
			content_item = cls.get_by_id(long(content_item_id))
			if content_item:
				return content_item
			else:
				logging.info("Invalid content id, cannot fetch content item.")
				return None

		@classmethod
		def get_content_items(cls, category_id):
			logging.info('Feteching all content items for category_id = %s', category_id)
			if category_id:
				content_items = cls.query(cls.category_id==str(category_id)).order(cls.sort_order).fetch()
				if content_items:
					logging.info("Returning content items..")
					return content_items
				else:
					logging.info("No content items exist for category = %s", category_id)
					return None
			else:
				logging.info("Invalid category iD, cannot fetch content items.")
				return None

		@classmethod
		def search_word (cls, search_string):
			print 'select * from ContentItem WHERE %s >= :1 AND %s < :2 order by %s limit 10'%('content','content', 'content')
			content_items =  ndb.gql(
			  'select * from ContentItem WHERE %s >= :1 AND %s < :2 order by %s limit 10'%('content','content', 'content'))
			resultlist = []
			for ci in content_items:
			  search_result = {}
			  search_result['id'] = ci.key.id()
			  search_result['name'] = ci.content
			  search_result['phone_no'] = ci.category_id
			  resultlist.append(search_result)
			return resultlist
