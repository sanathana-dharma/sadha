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




class Sentence(ndb.Model):
		"""Represents one line Basic building block of a sooktha, sloka etc
		Levels examples:
		Ramayana (ithihasa/grantha/mahakavya)  khand ->  adhyaya ->  sarga ->  sloka
		Vedas:  samhitha ->   mandala ->  ashtaka  ->  sookta ->  mantra

		"""
		content = ndb.StringProperty(required=True)
		sort_order = ndb.IntegerProperty(default=0)
		category_id = ndb.StringProperty(required=True)
		created_time = ndb.DateTimeProperty(auto_now_add=True)
		updated_time = ndb.DateTimeProperty(auto_now=True)