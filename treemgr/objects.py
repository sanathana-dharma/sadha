from treemgr import model_datastore
import utils
from utils import Error
from search import objects as search_objects
import config

TREE_INDEX_NAME = 'tree'

class clsBranch:
	def __init__(self):
		self.id = None
		self.name = None
		self.branch_parent_id = None
		self.sortorder = None

	def set(self, name, branch_parent_id, sortorder):
		self.id = None
		self.name = name
		self.branch_parent_id = branch_parent_id
		self.sortorder = sortorder

	def populate_from_record(self, branch):
		self.id = branch.id
		self.name = branch['name']
		self.branch_parent_id = branch['branch_parent_id']
		self.sortorder = branch['sortorder']

	def create(self):
		#Save object in Datastore
		entity = model_datastore.add(self)
		self.id = entity.id

		#Save object in elasticsearch
		esobj = search_objects.clsElasticIndex()
		if esobj.create_update_branch(TREE_INDEX_NAME,self):
			print("Saved branch to Elastic!")
			return True

		#self.add_to_index()
		return entity

	def update(self):
		if self.id:
			#Update in datastore
			entity = model_datastore.update(self)

			#Update data in Elasticindex
			esobj = search_objects.clsElasticIndex()
			if esobj.create_update_branch(TREE_INDEX_NAME,self):
				print("Updated branch to Elastic!")
				return True
			return False
		else:
			raise Error("*** clsBranch.update: Error! No valid ID provided for branch update, aborting.")

	def delete(self):
		if self.id:
			#Delete data in datastore
			model_datastore.delete(self)
			#Delete data in Elastic
			esobj = search_objects.clsElasticIndex()
			esobj.delete(TREE_INDEX_NAME, self.id)
			return
		else:
			raise Error("*** clsBranch.delete: Error! No valid ID provided for branch deletion, aborting.")

	def read(self, branch_id):
		branch = model_datastore.read(branch_id)
		self.name = branch['name']
		self.branch_parent_id = branch['branch_parent_id']
		self.sortorder = branch['sortorder']
		self.id = branch.id
		return self

	def get_next_sortorder(self):
		return model_datastore.get_next_sortorder(self.branch_parent_id)

	def get_next_record(self):
		return model_datastore.get_next_record(self.id, self.branch_parent_id)

	def get_pagination_data(cursor):
		records, cursor = model_datastore.get_pagination_data("Branch",cursor,10)
		return records, cursor

	def add_to_index(self):
		#Add object to index
		dict_indexed_object = self.generate_index_object()
		print("Adding to index, indexed object=")
		print(dict_indexed_object)
		s = objects.clsSearch()
		taskID = s.add_to_index(config.DICT_SEARCH_INDEXES[TREE_INDEX_NAME], dict_indexed_object)

	def update_data_in_index(self):
		#Delete current object in the index
		#Add new object to the index
		dict_indexed_object = self.generate_index_object()
		print("Updating index, indexed object=")
		print(dict_indexed_object)
		s = objects.clsSearch()
		taskID = s.update_data_in_index(config.DICT_SEARCH_INDEXES[TREE_INDEX_NAME], dict_indexed_object)

	def delete_data_in_index(self):
		#Delete current object in the index
		print("Deleting data in index, indexed object=")
		s = objects.clsSearch()
		taskID = s.delete_data_in_index(config.DICT_SEARCH_INDEXES[TREE_INDEX_NAME], self.id)

	def generate_index_object(self):
		#Generate tree path
		lstpath = utils.get_tree_path(self.id)
		pathtext = ""
		branch_ancestor_name = ""	#This is the main name of the branch

		if lstpath=="Home":
			pathtext = "Home"
			branch_ancestor_name = "Root"
		else:
			pathtext = ""
			try:
				dict = lstpath[1]
				branch_ancestor_name = dict['name']
			except:
				branch_ancestor_name = "Root"
			for item in lstpath:
				pathtext = pathtext + item['name'] + " > "

		#Create a single object suitable for indexing based on our data
		data = {
		"branch name": self.name,
		"branch ancestor name": branch_ancestor_name,
		"permalink": "/admin/contentmgr/view/" + str(self.id),
		"path": pathtext,
		"objectID": self.id

		}
		return data
