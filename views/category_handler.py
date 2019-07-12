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

# HANDLER FOR CATEGORIES


#API for fetching category details
class API_CategoryList(base_handler.BaseHandler):
  def get(self):
			#get child categories or fetch ROOT categories if no parameter was passed

			parent_category_id = self.request.get('parent_category_id')
			logging.info('parent_category_id= %s',parent_category_id)
			if parent_category_id:
				#Fetch child categories
				logging.info('Fetch child categories..')
				categories = models.Category.get_child_categories(parent_category_id)
			else:
				#Fetch all categories
				logging.info('Fetch root categories..')
				categories = models.Category.get_root_categories()

			dict_categories = {}
			if categories:
				#Lets package the data and send it out
				dict_categories = {cat.key.id(): cat.name for cat in categories}
				self.response.content_type = 'application/json'
				self.response.out.write(json.dumps( {'dict_categories': dict_categories}))


# API FOR CATEGORIES
class CategoryListHandler(base_handler.BaseHandler):
  def get(self):
	  		#Simply load the HTML Page
			context = {}
			self.render_response('categories-list.html',**context)

			'''
			#get child categories or fetch all categories if no parameter was passed
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
				#Render to UI
				for cat in categories:
					dict_categories[cat.key.id()] = cat
				#logging.info(dict_categories)
				context = {'dict_categories': dict_categories}
				self.render_response('categories-list.html',**context)
			else:
				context = {'dict_categories': dict_categories}
				self.render_response('categories-list.html',**context)
			'''


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




class AddCategoryHandler(base_handler.BaseHandler):
		def get(self):
			parent_category_id = self.request.get('parent_category_id')
			if parent_category_id == None or parent_category_id == '':
				parent_category_id = ''
				parent_category_name = ''
			else:
				parent_category = models.Category.get_category(parent_category_id)
				parent_category_name = parent_category.name

			context = {'parent_category_id': parent_category_id, 'parent_category_name': parent_category_name}
			self.render_response('categories-add-category.html',**context)

		def post(self):
			msg = ''
			category_name = self.request.get('category_name')
			parent_category_id = self.request.get('parent_category_id')
			logging.info('category_name=' + category_name)
			logging.info('parent_category_id=' + parent_category_id)

			try:
				category = models.Category.add_category(category_name,parent_category_id)
				if category:
					logging.info('Category added succesfully.')
				else:
					logging.info('Unable to add Category.')
			except Exception as e:
				msg = 'Problem in adding category to database. %s' % str(e)
			return self.response.out.write(json.dumps({'msg': msg}))

class EditCategoryHandler(base_handler.BaseHandler):
		def get(self):
			category_id = self.request.get('selected_category_id')
			msg = ''
			#try:
			category_selected = models.Category.get_category(category_id)
			if category_selected:
				parent_category = None
				if category_selected.parent_category_id == None:
					#This is a Root category, hence no parent exists
					logging.info('Root category - no parent found!')
				else:
					#This is a child category
					parent_category = models.Category.get_by_id(long(category_selected.parent_category_id))
					if parent_category:
						logging.info('Found Parent category')
					else:
						logging.error('Invalid Parent category!!')
			else:
				logging.error('Invalid category selected for editing!')

			if parent_category:
				context = {'category_selected_id': category_selected.key.id(),
				'category_selected_name': category_selected.name,'parent_category_name': parent_category.name}
			else:
				context = {'category_selected_id': category_selected.key.id(),
				'category_selected_name': category_selected.name,'parent_category_name': 'None'}

			self.render_response('categories-edit-category.html',**context)


		def post(self):
			msg = ''
			category_name_new = self.request.get('category_name_new')
			category_id = self.request.get('category_id')
			logging.info('category_name_new=' + category_name_new)
			logging.info('category_id=' + category_id)

			if not category_name_new:
				msg = 'Invalid Category name, please try again'

			if not category_id:
				msg = msg + ', Invalid Category selected for update.'


			try:
				models.Category.edit_category(category_id, category_name_new)
				logging.info('Category updated succesfully.')
			except Exception as e:
				msg = 'Problem in updating category to database.%s' % str(e)
			return self.response.out.write(json.dumps({'error_msg': msg}))






class AccountListHandler(base_handler.BaseHandler):
  def get(self):
    query = models.Accounts.get_accounts_pages()
    pgno = int(self.request.get('page', 1))
    pager = ndbpager.Pager(query=query, page=pgno)
    accounts, _, _ = pager.paginate(page_size=PAGE_SIZE)
    member_ids = [account.account_admin_member_id for account in accounts]
    members = models.Members.get_members_by_ids(member_ids)
    pageno = (pgno-1)*PAGE_SIZE
    context = {'accounts': accounts, 'members': members,
               'pager':pager,'path':self.request.path,
               'qs':dict(self.request.params),'pageno':pageno}
    self.render_response('accounts-list.html',**context)

  def post(self):
    msg = ''
    try:
      account_recs = models.Accounts.get_accounts()
    except Exception as e:
      msg = 'Error in fetching accounts.'
    accounts = {ac.key.id(): ac.name for ac in account_recs}
    self.response.content_type = 'application/json'
    self.response.out.write(json.dumps( {'accounts': accounts, 'err_msg': msg}))
